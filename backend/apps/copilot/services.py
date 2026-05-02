from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from apps.knowledge.services import test_knowledge_retrieval

from .audit import record_activity_audit, record_ai_audit
from .models import (
    AIAuditAction,
    CopilotConfidence,
    CopilotFeedback,
    CopilotMessage,
    CopilotMessageRole,
    CopilotProvider,
    CopilotSession,
    CopilotSessionStatus,
)
from .permissions import owns_assistant_message, require_student_user
from .prompts import SYSTEM_PROMPT, prompt_context_preview
from .providers import ProviderResult, get_copilot_provider
from .safety import (
    PROVIDER_UNAVAILABLE_ANSWER,
    REGISTRAR_DISCLAIMER,
    UNSUPPORTED_ANSWER,
    confidence_from_sources,
    ensure_registrar_fallback,
    looks_like_prompt_injection,
    redact_metadata,
    redact_text,
    validate_question_text,
)
from .selectors import build_safe_student_context, shape_source_references
from .suggestions import suggested_next_actions_for_question


@dataclass(frozen=True)
class CopilotAnswer:
    session: CopilotSession
    user_message: CopilotMessage
    assistant_message: CopilotMessage
    answer: str
    confidence: str
    sources: list[dict[str, Any]]
    suggested_next_actions: list[dict[str, str]]
    disclaimer: str


@transaction.atomic
def create_copilot_session(*, user, title: str = "", metadata: dict[str, Any] | None = None) -> CopilotSession:
    student = require_student_user(user)
    cleaned_title = (title or "").strip()[:120] or "New co-pilot chat"
    return CopilotSession.objects.create(
        user=user,
        student=student,
        title=cleaned_title,
        metadata=redact_metadata(metadata or {}),
    )


@transaction.atomic
def archive_copilot_session(*, user, session_id) -> CopilotSession:
    require_student_user(user)
    session = get_object_or_404(CopilotSession.objects.filter(user=user), pk=session_id)
    session.status = CopilotSessionStatus.ARCHIVED
    session.save(update_fields=["status", "updated_at"])
    return session


def get_session_for_user_or_404(*, user, session_id) -> CopilotSession:
    require_student_user(user)
    return get_object_or_404(CopilotSession.objects.filter(user=user), pk=session_id)


@transaction.atomic
def answer_copilot_question(*, user, question: str, session_id=None, request=None) -> CopilotAnswer:
    student = require_student_user(user)
    cleaned_question = validate_question_text(question)
    started = time.monotonic()
    session = _get_or_create_session_for_question(user=user, student=student, question=cleaned_question, session_id=session_id)
    safe_context = build_safe_student_context(student, user=user)
    prompt_preview = prompt_context_preview(safe_context)
    user_message = _create_message(
        session=session,
        role=CopilotMessageRole.USER,
        content=cleaned_question,
        confidence=CopilotConfidence.UNSUPPORTED,
        provider=CopilotProvider.SYSTEM,
        metadata={"promptInjectionFlagged": looks_like_prompt_injection(cleaned_question)},
    )
    record_ai_audit(
        action=AIAuditAction.COPILOT_QUERY,
        user=user,
        student=student,
        session=session,
        message=user_message,
        input_text=cleaned_question,
        metadata={"questionLength": len(cleaned_question)},
    )

    retrieval_results: list[dict[str, Any]] = []
    retrieval_error = ""
    if not looks_like_prompt_injection(cleaned_question):
        try:
            retrieval_results = test_knowledge_retrieval(
                cleaned_question,
                limit=_max_context_chunks(),
                actor=user,
                request=request,
            )
        except Exception as exc:
            retrieval_error = redact_text(str(exc), max_length=500)

    sources = shape_source_references(retrieval_results)
    source_confidence = confidence_from_sources(sources)
    provider_result: ProviderResult
    action = AIAuditAction.COPILOT_RESPONSE

    if retrieval_error:
        provider_result = ProviderResult(
            answer=PROVIDER_UNAVAILABLE_ANSWER,
            confidence=CopilotConfidence.LOW,
            provider=CopilotProvider.SYSTEM,
            model_name="retrieval-fallback",
            metadata={"retrievalError": retrieval_error},
        )
        action = AIAuditAction.COPILOT_PROVIDER_ERROR
        sources = []
    elif looks_like_prompt_injection(cleaned_question):
        provider_result = ProviderResult(
            answer=UNSUPPORTED_ANSWER,
            confidence=CopilotConfidence.UNSUPPORTED,
            provider=CopilotProvider.SYSTEM,
            model_name="safety-fallback",
            metadata={"promptInjectionFlagged": True},
        )
        action = AIAuditAction.COPILOT_LOW_CONFIDENCE
        sources = []
    elif not sources:
        provider_result = ProviderResult(
            answer=UNSUPPORTED_ANSWER,
            confidence=CopilotConfidence.UNSUPPORTED,
            provider=CopilotProvider.DETERMINISTIC,
            model_name="no-source-fallback",
            metadata={"reason": "no_sources"},
        )
        action = AIAuditAction.COPILOT_LOW_CONFIDENCE
    else:
        try:
            provider = get_copilot_provider()
            provider_result = provider.generate(
                question=cleaned_question,
                retrieved_chunks=retrieval_results,
                safe_student_context=safe_context,
                system_prompt=SYSTEM_PROMPT,
            )
        except Exception as exc:
            provider_result = ProviderResult(
                answer=PROVIDER_UNAVAILABLE_ANSWER,
                confidence=CopilotConfidence.LOW,
                provider=CopilotProvider.OPENAI_COMPATIBLE,
                model_name="provider-fallback",
                metadata={"providerError": redact_text(str(exc), max_length=500)},
            )
            action = AIAuditAction.COPILOT_PROVIDER_ERROR

    final_confidence = _merge_confidence(source_confidence, provider_result.confidence, bool(sources))
    answer = provider_result.answer
    if final_confidence in {CopilotConfidence.LOW, CopilotConfidence.UNSUPPORTED}:
        answer = ensure_registrar_fallback(answer)
        action = AIAuditAction.COPILOT_LOW_CONFIDENCE if action == AIAuditAction.COPILOT_RESPONSE else action

    latency_ms = int((time.monotonic() - started) * 1000)
    suggested_actions = suggested_next_actions_for_question(cleaned_question, sources=sources, confidence=final_confidence)
    assistant_message = _create_message(
        session=session,
        role=CopilotMessageRole.ASSISTANT,
        content=answer,
        safe_content=answer,
        source_references=sources,
        confidence=final_confidence,
        provider=provider_result.provider,
        model_name=provider_result.model_name,
        retrieval_query=cleaned_question,
        retrieved_chunk_count=len(sources),
        latency_ms=latency_ms,
        metadata={
            **redact_metadata(provider_result.metadata),
            "promptContextPreview": prompt_preview,
            "suggestedNextActions": suggested_actions,
        },
    )
    record_ai_audit(
        action=action,
        user=user,
        student=student,
        session=session,
        message=assistant_message,
        input_text=cleaned_question,
        output_text=answer,
        source_count=len(sources),
        confidence=final_confidence,
        provider=provider_result.provider,
        model_name=provider_result.model_name,
        metadata={
            "sourceIds": [source["sourceId"] for source in sources],
            "chunkIds": [source["chunkId"] for source in sources],
            "latencyMs": latency_ms,
            **redact_metadata(provider_result.metadata),
        },
    )
    record_activity_audit(
        user=user,
        action=action,
        summary=f"Student co-pilot interaction recorded with {final_confidence} confidence.",
        session=session,
        message=assistant_message,
        source_count=len(sources),
        request=request,
    )
    return CopilotAnswer(
        session=session,
        user_message=user_message,
        assistant_message=assistant_message,
        answer=answer,
        confidence=final_confidence,
        sources=sources,
        suggested_next_actions=suggested_actions,
        disclaimer=REGISTRAR_DISCLAIMER,
    )


@transaction.atomic
def rate_copilot_message(*, user, message_id, rating: str, comment: str = "") -> CopilotFeedback:
    require_student_user(user)
    message = get_object_or_404(CopilotMessage.objects.select_related("session"), pk=message_id)
    if not owns_assistant_message(user, message):
        raise NotFound("Message not found.")
    feedback, _ = CopilotFeedback.objects.update_or_create(
        message=message,
        user=user,
        defaults={
            "rating": rating,
            "comment": redact_text(comment or "", max_length=1000),
            "metadata": {"officialRecordEffect": False},
        },
    )
    return feedback


def _get_or_create_session_for_question(*, user, student, question: str, session_id=None) -> CopilotSession:
    if session_id:
        return get_object_or_404(CopilotSession.objects.filter(user=user), pk=session_id)
    title = question[:72].strip()
    if len(question) > 72:
        title = f"{title}..."
    return CopilotSession.objects.create(user=user, student=student, title=title or "New co-pilot chat")


def _create_message(
    *,
    session: CopilotSession,
    role: str,
    content: str,
    safe_content: str = "",
    source_references: list[dict[str, Any]] | None = None,
    confidence: str = CopilotConfidence.UNSUPPORTED,
    provider: str = CopilotProvider.SYSTEM,
    model_name: str = "",
    retrieval_query: str = "",
    retrieved_chunk_count: int = 0,
    latency_ms: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> CopilotMessage:
    message = CopilotMessage.objects.create(
        session=session,
        role=role,
        content=redact_text(content, max_length=8000),
        safe_content=redact_text(safe_content, max_length=8000) if safe_content else "",
        source_references=redact_metadata({"sources": source_references or []})["sources"],
        confidence=confidence,
        provider=provider,
        model_name=model_name,
        retrieval_query=redact_text(retrieval_query, max_length=1000),
        retrieved_chunk_count=retrieved_chunk_count,
        latency_ms=latency_ms,
        metadata=redact_metadata(metadata or {}),
    )
    session.last_message_at = message.created_at
    session.save(update_fields=["last_message_at", "updated_at"])
    return message


def _max_context_chunks() -> int:
    return max(1, min(int(getattr(settings, "AI_MAX_CONTEXT_CHUNKS", 5)), 10))


def _merge_confidence(source_confidence: str, provider_confidence: str, has_sources: bool) -> str:
    if not has_sources:
        return CopilotConfidence.UNSUPPORTED
    if source_confidence == CopilotConfidence.LOW or provider_confidence == CopilotConfidence.LOW:
        return CopilotConfidence.LOW
    if source_confidence == CopilotConfidence.HIGH:
        return CopilotConfidence.HIGH
    if provider_confidence == CopilotConfidence.UNSUPPORTED:
        return CopilotConfidence.UNSUPPORTED
    return CopilotConfidence.MEDIUM
