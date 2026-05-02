from __future__ import annotations

from typing import Any

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely

from .models import AIAuditLog, CopilotConfidence, CopilotMessage, CopilotProvider, CopilotSession
from .safety import redact_metadata, redact_text


def record_ai_audit(
    *,
    action: str,
    user,
    student,
    session: CopilotSession | None = None,
    message: CopilotMessage | None = None,
    input_text: str = "",
    output_text: str = "",
    source_count: int = 0,
    confidence: str = CopilotConfidence.UNSUPPORTED,
    provider: str = CopilotProvider.SYSTEM,
    model_name: str = "",
    metadata: dict[str, Any] | None = None,
) -> AIAuditLog:
    return AIAuditLog.objects.create(
        user=user if getattr(user, "pk", None) else None,
        student=student,
        session=session,
        message=message,
        action=action,
        input_text=redact_text(input_text, max_length=8000),
        output_text=redact_text(output_text, max_length=8000),
        source_count=source_count,
        confidence=confidence,
        provider=provider,
        model_name=model_name,
        metadata=redact_metadata(metadata or {}),
    )


def record_activity_audit(
    *,
    user,
    action: str,
    summary: str,
    session: CopilotSession,
    message: CopilotMessage,
    source_count: int,
    request=None,
) -> None:
    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action=action,
        summary=summary,
        target_type="CopilotMessage",
        target_id=str(message.id),
        severity=AuditSeverity.INFO,
        metadata={
            "sessionId": str(session.id),
            "messageId": str(message.id),
            "sourceCount": source_count,
            "officialRecord": False,
        },
        request=request,
    )
