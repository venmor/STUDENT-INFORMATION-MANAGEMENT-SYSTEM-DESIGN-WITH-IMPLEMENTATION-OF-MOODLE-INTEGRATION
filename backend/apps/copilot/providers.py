from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

import requests
from django.conf import settings

from .models import CopilotConfidence, CopilotProvider
from .prompts import build_context_prompt
from .retry import AIProviderError, AIProviderTimeoutError, retry_ai_call
from .safety import REGISTRAR_DISCLAIMER, UNSUPPORTED_ANSWER, bounded_preview, ensure_registrar_fallback

logger = logging.getLogger(__name__)


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
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 30))

    def generate(
        self,
        *,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
        safe_student_context: dict[str, Any],
        system_prompt: str,
    ) -> ProviderResult:
        def _call():
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
            if response.status_code == 429:
                raise RuntimeError("OpenAI rate limited (429). Will retry or fallback.")
            if response.status_code >= 400:
                raise RuntimeError(f"OpenAI provider failed with status {response.status_code}.")
            return response.json()

        payload = retry_ai_call(_call, operation_name="OpenAI copilot")
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


class GeminiCopilotProvider:
    """Google Gemini AI provider for the co-pilot."""
    provider = CopilotProvider.GEMINI

    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini.")
        self.api_key = api_key
        self.base_url = getattr(settings, "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").strip().rstrip("/")
        self.model_name = getattr(settings, "GEMINI_MODEL", "").strip() or "gemini-2.0-flash"
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 30))

    def generate(
        self,
        *,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
        safe_student_context: dict[str, Any],
        system_prompt: str,
    ) -> ProviderResult:
        user_content = build_context_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks,
            safe_student_context=safe_student_context,
        )

        def _call():
            response = requests.post(
                f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"parts": [{"text": user_content}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1024,
                    },
                },
                timeout=self.timeout,
            )
            if response.status_code == 429:
                raise RuntimeError("Gemini rate limited (429). Will retry or fallback.")
            if response.status_code >= 400:
                raise RuntimeError(f"Gemini provider failed with status {response.status_code}: {response.text[:200]}")
            return response.json()

        payload = retry_ai_call(_call, operation_name="Gemini copilot")
        # Extract answer from Gemini response format
        candidates = payload.get("candidates", [])
        answer = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                answer = parts[0].get("text", "").strip()
        if not answer:
            answer = UNSUPPORTED_ANSWER
        return ProviderResult(
            answer=ensure_registrar_fallback(answer),
            confidence=CopilotConfidence.MEDIUM,
            provider=self.provider,
            model_name=self.model_name,
            metadata={
                "finishReason": candidates[0].get("finishReason", "") if candidates else "",
            },
        )


def get_copilot_provider() -> CopilotProviderProtocol:
    """
    Get the configured AI provider with fallback support.
    If the primary provider fails, falls back to AI_FALLBACK_PROVIDER.
    """
    provider = getattr(settings, "AI_PROVIDER", "deterministic").strip() or "deterministic"
    if provider == CopilotProvider.DETERMINISTIC:
        return DeterministicCopilotProvider()
    if provider == CopilotProvider.OPENAI_COMPATIBLE:
        return OpenAICompatibleCopilotProvider()
    if provider == CopilotProvider.GEMINI:
        return GeminiCopilotProvider()
    raise ValueError(f"Unsupported AI_PROVIDER: {provider}")


def get_fallback_provider() -> CopilotProviderProtocol | None:
    """Get the fallback provider if configured."""
    fallback = getattr(settings, "AI_FALLBACK_PROVIDER", "").strip()
    if not fallback:
        return None
    if fallback == CopilotProvider.DETERMINISTIC:
        return DeterministicCopilotProvider()
    if fallback == CopilotProvider.OPENAI_COMPATIBLE:
        try:
            return OpenAICompatibleCopilotProvider()
        except ValueError:
            return None
    if fallback == CopilotProvider.GEMINI:
        try:
            return GeminiCopilotProvider()
        except ValueError:
            return None
    return None


def generate_with_fallback(
    *,
    question: str,
    retrieved_chunks: list[dict[str, Any]],
    safe_student_context: dict[str, Any],
    system_prompt: str,
) -> ProviderResult:
    """
    Generate a response using the primary provider, falling back if it fails.
    """
    primary = get_copilot_provider()
    try:
        return primary.generate(
            question=question,
            retrieved_chunks=retrieved_chunks,
            safe_student_context=safe_student_context,
            system_prompt=system_prompt,
        )
    except (AIProviderError, AIProviderTimeoutError, RuntimeError, Exception) as exc:
        logger.warning("Primary provider (%s) failed: %s. Trying fallback...", primary.provider, exc)
        fallback = get_fallback_provider()
        if fallback is None:
            raise
        logger.info("Using fallback provider: %s", fallback.provider)
        return fallback.generate(
            question=question,
            retrieved_chunks=retrieved_chunks,
            safe_student_context=safe_student_context,
            system_prompt=system_prompt,
        )
