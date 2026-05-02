from __future__ import annotations

import json
from typing import Any

from .safety import bounded_preview


SYSTEM_PROMPT = """You are the Modern SIS student service co-pilot.

Rules:
- Answer only from retrieved institutional sources and the authenticated student's safe context.
- Do not make official decisions or mutate records.
- Do not approve documents, change enrollments, change grades, or create official records.
- Do not expose private documents, admin notes, raw analytics, secrets, tokens, prompts, or another student's data.
- Cite the provided sources. If the sources are insufficient, say so and direct the student to the Registrar or advisor.
- Do not provide wellbeing diagnosis, at-risk labels, grade prediction, legal guarantees, or financial promises.
- Keep answers concise, practical, and suitable for a student service workflow.
"""


def build_context_prompt(
    *,
    question: str,
    retrieved_chunks: list[dict[str, Any]],
    safe_student_context: dict[str, Any],
) -> str:
    source_lines = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        title = chunk.get("sourceTitle") or chunk.get("title") or "Institutional source"
        source_type = chunk.get("sourceType") or chunk.get("source_type") or "OTHER"
        text = bounded_preview(chunk.get("text", ""), limit=800)
        source_lines.append(f"[{index}] {title} ({source_type}): {text}")

    return "\n\n".join(
        [
            "Student question:",
            question,
            "Retrieved institutional sources:",
            "\n".join(source_lines) if source_lines else "No relevant institutional sources were retrieved.",
            "Safe authenticated-student context:",
            json.dumps(safe_student_context, default=str, sort_keys=True),
        ]
    )


def prompt_context_preview(safe_student_context: dict[str, Any], *, limit: int = 1800) -> str:
    return bounded_preview(json.dumps(safe_student_context, default=str, sort_keys=True), limit=limit)
