from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

import requests
from django.conf import settings

from .prompts import SUMMARISATION_SYSTEM_PROMPT


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
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 20))

    def summarise(self, raw_text: str) -> SummarisationResult:
        started = time.monotonic()
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
        latency_ms = int((time.monotonic() - started) * 1000)
        if response.status_code >= 400:
            raise RuntimeError(f"Summarisation provider failed with status {response.status_code}.")
        payload = response.json()
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


def get_summarisation_provider():
    provider = getattr(settings, "AI_PROVIDER", "deterministic").strip() or "deterministic"
    if provider == "deterministic":
        return DeterministicSummarisationProvider()
    if provider == "openai_compatible":
        return OpenAISummarisationProvider()
    raise ValueError(f"Unsupported AI_PROVIDER for summarisation: {provider}")
