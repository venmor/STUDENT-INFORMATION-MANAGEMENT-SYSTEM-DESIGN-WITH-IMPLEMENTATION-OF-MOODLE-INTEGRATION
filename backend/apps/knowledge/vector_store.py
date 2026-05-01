from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Callable

import requests
from django.conf import settings


class VectorStoreUnavailable(RuntimeError):
    pass


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    dot = sum(left[index] * right[index] for index in range(size))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class InMemoryVectorStore:
    _collections: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    def __init__(self, *, collection_name: str):
        self.collection_name = collection_name

    def ensure_collection(self, vector_size: int | None = None) -> None:
        self._collections.setdefault(self.collection_name, {})

    def upsert_chunks(self, chunks: list[dict[str, Any]]) -> int:
        collection = self._collections.setdefault(self.collection_name, {})
        for chunk in chunks:
            collection[str(chunk["id"])] = chunk
        return len(chunks)

    def search(self, query_vector: list[float], *, limit: int = 5, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        rows = []
        for chunk_id, chunk in self._collections.get(self.collection_name, {}).items():
            metadata = chunk.get("metadata", {})
            if filters.get("sourceType") and metadata.get("sourceType") != filters["sourceType"]:
                continue
            rows.append(
                {
                    "id": chunk_id,
                    "score": cosine_similarity(query_vector, chunk.get("vector", [])),
                    "text": chunk.get("text", ""),
                    "metadata": metadata,
                }
            )
        return sorted(rows, key=lambda row: row["score"], reverse=True)[:limit]

    def delete_source(self, source_id: str) -> int:
        collection = self._collections.setdefault(self.collection_name, {})
        to_delete = [chunk_id for chunk_id, chunk in collection.items() if chunk.get("metadata", {}).get("sourceId") == str(source_id)]
        for chunk_id in to_delete:
            del collection[chunk_id]
        return len(to_delete)

    def health_check(self, *, raise_on_error: bool = False) -> dict[str, Any]:
        return {"healthy": True, "message": "In-memory vector store is ready.", "provider": "memory"}


class QdrantVectorStore:
    def __init__(
        self,
        *,
        base_url: str,
        collection_name: str,
        request_func: Callable[..., Any] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.collection_name = collection_name
        self.request = request_func or requests.request

    def ensure_collection(self, vector_size: int | None = None) -> None:
        size = int(vector_size or getattr(settings, "EMBEDDING_VECTOR_SIZE", 64))
        try:
            response = self.request(
                "PUT",
                f"{self.base_url}/collections/{self.collection_name}",
                json={"vectors": {"size": size, "distance": "Cosine"}},
                timeout=10,
            )
        except Exception as exc:
            raise VectorStoreUnavailable(f"Qdrant is unavailable at {self.base_url}: {exc}") from exc
        if getattr(response, "status_code", 500) == 409:
            return
        if getattr(response, "status_code", 500) >= 400:
            raise VectorStoreUnavailable(f"Qdrant collection setup failed with status {response.status_code}.")

    def upsert_chunks(self, chunks: list[dict[str, Any]]) -> int:
        points = [
            {
                "id": str(chunk["id"]),
                "vector": chunk["vector"],
                "payload": {
                    **chunk.get("metadata", {}),
                    "text": chunk.get("text", ""),
                },
            }
            for chunk in chunks
        ]
        try:
            response = self.request(
                "PUT",
                f"{self.base_url}/collections/{self.collection_name}/points",
                params={"wait": "true"},
                json={"points": points},
                timeout=20,
            )
        except Exception as exc:
            raise VectorStoreUnavailable(f"Qdrant is unavailable at {self.base_url}: {exc}") from exc
        if getattr(response, "status_code", 500) >= 400:
            raise VectorStoreUnavailable(f"Qdrant upsert failed with status {response.status_code}.")
        return len(points)

    def search(self, query_vector: list[float], *, limit: int = 5, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        qdrant_filter = None
        if filters and filters.get("sourceType"):
            qdrant_filter = {"must": [{"key": "sourceType", "match": {"value": filters["sourceType"]}}]}
        try:
            response = self.request(
                "POST",
                f"{self.base_url}/collections/{self.collection_name}/points/search",
                json={"vector": query_vector, "limit": limit, "with_payload": True, "filter": qdrant_filter},
                timeout=20,
            )
        except Exception as exc:
            raise VectorStoreUnavailable(f"Qdrant is unavailable at {self.base_url}: {exc}") from exc
        if getattr(response, "status_code", 500) >= 400:
            raise VectorStoreUnavailable(f"Qdrant search failed with status {response.status_code}.")
        return [
            {
                "id": str(row.get("id")),
                "score": float(row.get("score") or 0),
                "text": row.get("payload", {}).get("text", ""),
                "metadata": row.get("payload", {}),
            }
            for row in response.json().get("result", [])
        ]

    def delete_source(self, source_id: str) -> int:
        try:
            response = self.request(
                "POST",
                f"{self.base_url}/collections/{self.collection_name}/points/delete",
                params={"wait": "true"},
                json={"filter": {"must": [{"key": "sourceId", "match": {"value": str(source_id)}}]}},
                timeout=20,
            )
        except Exception as exc:
            raise VectorStoreUnavailable(f"Qdrant is unavailable at {self.base_url}: {exc}") from exc
        if getattr(response, "status_code", 500) >= 400:
            raise VectorStoreUnavailable(f"Qdrant delete failed with status {response.status_code}.")
        return 0

    def health_check(self, *, raise_on_error: bool = False) -> dict[str, Any]:
        try:
            response = self.request("GET", f"{self.base_url}/collections/{self.collection_name}", timeout=5)
        except Exception as exc:
            if raise_on_error:
                raise VectorStoreUnavailable(f"Qdrant is unavailable at {self.base_url}: {exc}") from exc
            return {"healthy": False, "message": f"Qdrant is unavailable at {self.base_url}.", "provider": "qdrant"}
        healthy = getattr(response, "status_code", 500) < 500
        if not healthy and raise_on_error:
            raise VectorStoreUnavailable(f"Qdrant health check failed with status {response.status_code}.")
        return {"healthy": healthy, "message": "Qdrant responded." if healthy else "Qdrant did not respond successfully.", "provider": "qdrant"}


def get_vector_store():
    provider = getattr(settings, "KNOWLEDGE_VECTOR_STORE_PROVIDER", "qdrant")
    collection = getattr(settings, "QDRANT_COLLECTION", "modern_sis_knowledge")
    if provider == "memory":
        return InMemoryVectorStore(collection_name=collection)
    if provider == "qdrant":
        return QdrantVectorStore(base_url=getattr(settings, "QDRANT_URL", "http://qdrant:6333"), collection_name=collection)
    raise ValueError(f"Unsupported KNOWLEDGE_VECTOR_STORE_PROVIDER: {provider}")
