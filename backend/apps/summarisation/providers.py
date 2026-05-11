from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

import requests
from django.conf import settings

from apps.copilot.retry import AIProviderError, AIProviderTimeoutError, retry_ai_call

from .prompts import SUMMARISATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SummarisationResult:
    key_issues: list[str]
    recommended_actions: list[str]
    urgency_level: str
    provider: str
    model_name: str
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


VALID_URGENCY_LEVELS = {"Routine", "Follow-up Needed", "Urgent"}


def _parse_structured_output(raw: str) -> dict[str, Any]:
    cleaned = raw.strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    parsed = json.loads(cleaned)
    if not isinstance(parsed.get("key_issues"), list):
        parsed["key_issues"] = []
    if not isinstance(parsed.get("recommended_actions"), list):
        parsed["recommended_actions"] = []
    urgency = parsed.get("urgency_level", "Routine")
    if urgency not in VALID_URGENCY_LEVELS:
        urgency = "Routine"
    parsed["urgency_level"] = urgency
    parsed["key_issues"] = [str(item) for item in parsed["key_issues"][:5]]
    parsed["recommended_actions"] = [str(item) for item in parsed["recommended_actions"][:5]]
    return parsed


class DeterministicSummarisationProvider:
    provider = "deterministic"
    model_name = "deterministic-summarisation-v1"

    def summarise(self, raw_text: str) -> SummarisationResult:
        sentences = [s.strip() for s in raw_text.replace("\n", ". ").split(".") if s.strip()]
        key_issues = sentences[:3] if sentences else ["No issues identified from input."]
        recommended_actions = ["Review notes with student.", "Schedule follow-up meeting."]
        urgency = "Routine"
        lower = raw_text.lower()
        if any(word in lower for word in ("urgent", "crisis", "emergency", "immediate")):
            urgency = "Urgent"
        elif any(word in lower for word in ("follow-up", "follow up", "concern", "struggling")):
            urgency = "Follow-up Needed"
        return SummarisationResult(
            key_issues=key_issues,
            recommended_actions=recommended_actions,
            urgency_level=urgency,
            provider=self.provider,
            model_name=self.model_name,
        )


class OpenAISummarisationProvider:
    provider = "openai_compatible"

    def __init__(self):
        api_key = getattr(settings, "OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai_compatible.")
        self.api_key = api_key
        self.base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
        self.model_name = getattr(settings, "OPENAI_MODEL", "").strip() or "gpt-4o-mini"
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 30))

    def summarise(self, raw_text: str) -> SummarisationResult:
        started = time.monotonic()

        def _call():
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": SUMMARISATION_SYSTEM_PROMPT},
                        {"role": "user", "content": raw_text},
                    ],
                    "temperature": 0.1,
                },
                timeout=self.timeout,
            )
            if response.status_code == 429:
                raise RuntimeError("OpenAI rate limited (429). Will retry or fallback.")
            if response.status_code >= 400:
                raise RuntimeError(f"Summarisation provider failed with status {response.status_code}.")
            return response.json()

        payload = retry_ai_call(_call, operation_name="OpenAI summarisation")
        latency_ms = int((time.monotonic() - started) * 1000)
        raw_content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = _parse_structured_output(raw_content)
        return SummarisationResult(
            key_issues=parsed["key_issues"],
            recommended_actions=parsed["recommended_actions"],
            urgency_level=parsed["urgency_level"],
            provider=self.provider,
            model_name=self.model_name,
            latency_ms=latency_ms,
            metadata={"finishReason": payload.get("choices", [{}])[0].get("finish_reason", "")},
        )


class GeminiSummarisationProvider:
    """Google Gemini AI provider for summarisation."""
    provider = "gemini"

    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini.")
        self.api_key = api_key
        self.base_url = getattr(settings, "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").strip().rstrip("/")
        self.model_name = getattr(settings, "GEMINI_MODEL", "").strip() or "gemini-2.0-flash"
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 30))

    def summarise(self, raw_text: str) -> SummarisationResult:
        started = time.monotonic()

        def _call():
            response = requests.post(
                f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "system_instruction": {"parts": [{"text": SUMMARISATION_SYSTEM_PROMPT}]},
                    "contents": [{"parts": [{"text": raw_text}]}],
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
                raise RuntimeError(f"Gemini summarisation failed with status {response.status_code}: {response.text[:200]}")
            return response.json()

        payload = retry_ai_call(_call, operation_name="Gemini summarisation")
        latency_ms = int((time.monotonic() - started) * 1000)

        # Extract text from Gemini response
        candidates = payload.get("candidates", [])
        raw_content = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                raw_content = parts[0].get("text", "")

        parsed = _parse_structured_output(raw_content)
        return SummarisationResult(
            key_issues=parsed["key_issues"],
            recommended_actions=parsed["recommended_actions"],
            urgency_level=parsed["urgency_level"],
            provider=self.provider,
            model_name=self.model_name,
            latency_ms=latency_ms,
            metadata={
                "finishReason": candidates[0].get("finishReason", "") if candidates else "",
            },
        )


def get_summarisation_provider():
    """Get the primary summarisation provider."""
    provider = getattr(settings, "AI_PROVIDER", "deterministic").strip() or "deterministic"
    if provider == "deterministic":
        return DeterministicSummarisationProvider()
    if provider == "openai_compatible":
        return OpenAISummarisationProvider()
    if provider == "gemini":
        return GeminiSummarisationProvider()
    raise ValueError(f"Unsupported AI_PROVIDER for summarisation: {provider}")


def get_fallback_summarisation_provider():
    """Get the fallback summarisation provider if configured."""
    fallback = getattr(settings, "AI_FALLBACK_PROVIDER", "").strip()
    if not fallback:
        return None
    if fallback == "deterministic":
        return DeterministicSummarisationProvider()
    if fallback == "openai_compatible":
        try:
            return OpenAISummarisationProvider()
        except ValueError:
            return None
    if fallback == "gemini":
        try:
            return GeminiSummarisationProvider()
        except ValueError:
            return None
    return None


def summarise_with_fallback(raw_text: str) -> SummarisationResult:
    """Summarise using the primary provider, falling back if it fails."""
    primary = get_summarisation_provider()
    try:
        return primary.summarise(raw_text)
    except (AIProviderError, AIProviderTimeoutError, RuntimeError, Exception) as exc:
        logger.warning("Primary summarisation provider (%s) failed: %s. Trying fallback...", primary.provider, exc)
        fallback = get_fallback_summarisation_provider()
        if fallback is None:
            raise
        logger.info("Using fallback summarisation provider: %s", fallback.provider)
        return fallback.summarise(raw_text)
