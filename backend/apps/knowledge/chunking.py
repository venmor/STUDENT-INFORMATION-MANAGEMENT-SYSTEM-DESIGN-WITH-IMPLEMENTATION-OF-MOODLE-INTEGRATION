from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str
    token_count: int


def chunk_text(text: str, *, chunk_tokens: int = 512, overlap_tokens: int = 64) -> list[TextChunk]:
    tokens = (text or "").split()
    if not tokens:
        return []
    safe_chunk_size = max(1, chunk_tokens)
    safe_overlap = max(0, min(overlap_tokens, safe_chunk_size - 1))
    step = safe_chunk_size - safe_overlap
    chunks: list[TextChunk] = []
    index = 0
    for start in range(0, len(tokens), step):
        window = tokens[start : start + safe_chunk_size]
        if not window:
            break
        chunks.append(TextChunk(chunk_index=index, text=" ".join(window), token_count=len(window)))
        index += 1
        if start + safe_chunk_size >= len(tokens):
            break
    return chunks
