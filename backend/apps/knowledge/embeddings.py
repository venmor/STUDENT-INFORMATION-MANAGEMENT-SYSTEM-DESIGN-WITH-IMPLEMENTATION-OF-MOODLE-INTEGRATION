from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

import requests
from django.conf import settings


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


class EmbeddingProvider(Protocol):
    dimension: int

    def embed_text(self, text: str) -> list[float]:
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class DeterministicEmbeddingProvider:
    def __init__(self, dimension: int = 64):
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in TOKEN_PATTERN.findall((text or "").lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 8) for value in vector]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, *, api_key: str, model: str, base_url: str = "https://api.openai.com/v1", timeout: int = 20):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai.")
        if not model:
            raise ValueError("EMBEDDING_MODEL is required when EMBEDDING_PROVIDER=openai.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.dimension = int(getattr(settings, "EMBEDDING_VECTOR_SIZE", 1536))

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "input": texts},
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Embedding provider request failed with status {response.status_code}.")
        payload = response.json()
        return [item["embedding"] for item in payload.get("data", [])]


def get_embedding_provider() -> EmbeddingProvider:
    provider = getattr(settings, "EMBEDDING_PROVIDER", "deterministic")
    if provider == "deterministic":
        return DeterministicEmbeddingProvider(dimension=int(getattr(settings, "EMBEDDING_VECTOR_SIZE", 64)))
    if provider == "openai":
        return OpenAICompatibleEmbeddingProvider(
            api_key=getattr(settings, "OPENAI_API_KEY", ""),
            model=getattr(settings, "EMBEDDING_MODEL", ""),
            base_url=getattr(settings, "OPENAI_EMBEDDING_BASE_URL", "https://api.openai.com/v1"),
            timeout=int(getattr(settings, "EMBEDDING_TIMEOUT", 20)),
        )
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")
