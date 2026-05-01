from __future__ import annotations

import pytest

from apps.knowledge.chunking import chunk_text
from apps.knowledge.embeddings import DeterministicEmbeddingProvider
from apps.knowledge.vector_store import InMemoryVectorStore, QdrantVectorStore, VectorStoreUnavailable


def test_chunk_text_uses_overlap_and_preserves_source_order():
    text = " ".join(f"token{i}" for i in range(130))

    chunks = chunk_text(text, chunk_tokens=50, overlap_tokens=10)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].text.split()[0] == "token40"
    assert chunks[2].text.split()[0] == "token80"
    assert chunks[0].token_count == 50


def test_deterministic_embedding_provider_returns_stable_vectors_without_network():
    provider = DeterministicEmbeddingProvider(dimension=32)

    first = provider.embed_text("What is the deadline to drop a course?")
    second = provider.embed_text("What is the deadline to drop a course?")
    different = provider.embed_text("How do I pay fees?")

    assert first == second
    assert first != different
    assert len(first) == 32
    assert all(isinstance(value, float) for value in first)


def test_in_memory_vector_store_retrieves_relevant_chunk():
    provider = DeterministicEmbeddingProvider(dimension=32)
    store = InMemoryVectorStore(collection_name="test")
    drop_text = "Students must drop a course before the published drop deadline in the academic calendar."
    fee_text = "Tuition fee schedules are published by the finance office."
    store.ensure_collection(vector_size=32)
    store.upsert_chunks(
        [
            {
                "id": "drop",
                "vector": provider.embed_text(drop_text),
                "text": drop_text,
                "metadata": {"sourceTitle": "Academic Calendar Deadline Guide"},
            },
            {
                "id": "fees",
                "vector": provider.embed_text(fee_text),
                "text": fee_text,
                "metadata": {"sourceTitle": "Fee Schedule"},
            },
        ]
    )

    results = store.search(provider.embed_text("What is the deadline to drop a course?"), limit=1)

    assert results[0]["id"] == "drop"
    assert results[0]["score"] > 0


def test_qdrant_vector_store_reports_unavailable_service(monkeypatch):
    def fail_request(*args, **kwargs):
        raise RuntimeError("connection refused")

    store = QdrantVectorStore(base_url="http://qdrant.invalid:6333", collection_name="test", request_func=fail_request)

    with pytest.raises(VectorStoreUnavailable, match="Qdrant is unavailable"):
        store.health_check(raise_on_error=True)


def test_qdrant_ensure_collection_is_idempotent_when_collection_exists():
    class ExistingCollectionResponse:
        status_code = 409

    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return ExistingCollectionResponse()

    store = QdrantVectorStore(base_url="http://qdrant.local:6333", collection_name="knowledge", request_func=request)

    store.ensure_collection(vector_size=64)

    assert calls[0][0] == "PUT"
