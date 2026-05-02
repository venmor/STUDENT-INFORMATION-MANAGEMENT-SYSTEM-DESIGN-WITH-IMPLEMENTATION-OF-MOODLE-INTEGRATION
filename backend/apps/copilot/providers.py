from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import requests
from django.conf import settings

from .models import CopilotConfidence, CopilotProvider
from .prompts import build_context_prompt
from .safety import REGISTRAR_DISCLAIMER, UNSUPPORTED_ANSWER, bounded_preview, ensure_registrar_fallback


@dataclass(frozen=True)
class ProviderResult:
    answer: str
    confidence: str
    provider: str = CopilotProvider.DETERMINISTIC
    model_name: str = "deterministic-source-grounded-v1"
    metadata: dict[str, Any] = field(default_factory=dict)


class CopilotProviderProtocol(Protocol):
    provider: str
    model_name: str

    def generate(
        self,
        *,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
        safe_student_context: dict[str, Any],
        system_prompt: str,
    ) -> ProviderResult:
        ...


class DeterministicCopilotProvider:
    provider = CopilotProvider.DETERMINISTIC
    model_name = "deterministic-source-grounded-v1"

    def generate(
        self,
        *,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
        safe_student_context: dict[str, Any],
        system_prompt: str,
    ) -> ProviderResult:
        if not retrieved_chunks:
            return ProviderResult(
                answer=UNSUPPORTED_ANSWER,
                confidence=CopilotConfidence.UNSUPPORTED,
                provider=self.provider,
                model_name=self.model_name,
            )

        lower_question = question.lower()
        source_summary = " ".join(bounded_preview(chunk.get("text", ""), limit=260) for chunk in retrieved_chunks[:2])
        student_lines = self._student_context_lines(lower_question, safe_student_context)
        answer_parts = ["Based on the retrieved institutional sources, " + source_summary]
        if student_lines:
            answer_parts.append("From your student context, " + " ".join(student_lines))
        answer_parts.append(REGISTRAR_DISCLAIMER)
        return ProviderResult(
            answer=" ".join(part.strip() for part in answer_parts if part.strip()),
            confidence=CopilotConfidence.MEDIUM,
            provider=self.provider,
            model_name=self.model_name,
            metadata={"mode": "deterministic", "sourceCount": len(retrieved_chunks)},
        )

    def _student_context_lines(self, question: str, context: dict[str, Any]) -> list[str]:
        lines: list[str] = []
        if any(word in question for word in ("course", "courses", "enrolled", "enrollment")):
            enrollments = context.get("currentEnrollments", [])
            if enrollments:
                labels = [f"{item.get('courseCode')} {item.get('sectionCode')}" for item in enrollments[:4]]
                lines.append(f"your current enrolled sections include {', '.join(labels)}.")
        if any(word in question for word in ("document", "rejected", "upload")):
            summary = context.get("documentStatusSummary", {})
            rejected = summary.get("REJECTED", 0)
            pending = summary.get("PENDING_REVIEW", 0)
            lines.append(f"your student-visible document summary shows {rejected} rejected and {pending} pending review document(s).")
        if any(word in question for word in ("grade", "grades", "transcript")):
            grade_summary = context.get("gradeSummary", {})
            lines.append(f"your safe grade summary shows {grade_summary.get('officialGradeCount', 0)} official grade record(s).")
        return lines


class OpenAICompatibleCopilotProvider:
    provider = CopilotProvider.OPENAI_COMPATIBLE

    def __init__(self):
        api_key = getattr(settings, "OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai_compatible.")
        self.api_key = api_key
        self.base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
        self.model_name = getattr(settings, "OPENAI_MODEL", "").strip() or "gpt-4o-mini"
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 20))

    def generate(
        self,
        *,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
        safe_student_context: dict[str, Any],
        system_prompt: str,
    ) -> ProviderResult:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": build_context_prompt(
                            question=question,
                            retrieved_chunks=retrieved_chunks,
                            safe_student_context=safe_student_context,
                        ),
                    },
                ],
                "temperature": 0.1,
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"OpenAI-compatible provider failed with status {response.status_code}.")
        payload = response.json()
        answer = payload.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not answer:
            answer = UNSUPPORTED_ANSWER
        return ProviderResult(
            answer=ensure_registrar_fallback(answer),
            confidence=CopilotConfidence.MEDIUM,
            provider=self.provider,
            model_name=self.model_name,
            metadata={"finishReason": payload.get("choices", [{}])[0].get("finish_reason", "")},
        )


def get_copilot_provider() -> CopilotProviderProtocol:
    provider = getattr(settings, "AI_PROVIDER", "deterministic").strip() or "deterministic"
    if provider == CopilotProvider.DETERMINISTIC:
        return DeterministicCopilotProvider()
    if provider == CopilotProvider.OPENAI_COMPATIBLE:
        return OpenAICompatibleCopilotProvider()
    raise ValueError(f"Unsupported AI_PROVIDER: {provider}")
