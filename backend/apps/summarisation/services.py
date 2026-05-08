from __future__ import annotations

import json
import time
from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely
from apps.copilot.audit import record_ai_audit
from apps.copilot.models import AIAuditAction, CopilotProvider
from apps.copilot.safety import redact_metadata, redact_text
from apps.students.models import AdvisingNote, AdvisingNoteStatus

from .models import SummarisationRequest, SummarisationStatus
from .prompts import MAX_INPUT_LENGTH
from .providers import SummarisationResult, get_summarisation_provider


def validate_input_text(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        raise serializers.ValidationError({"raw_text": "Input text is required."})
    if len(cleaned) > MAX_INPUT_LENGTH:
        raise serializers.ValidationError(
            {"raw_text": f"Input must be {MAX_INPUT_LENGTH} characters or fewer. Current: {len(cleaned)}."}
        )
    return cleaned


@transaction.atomic
def create_summarisation_request(
    *,
    user,
    raw_text: str,
    student=None,
    request=None,
) -> SummarisationRequest:
    cleaned = validate_input_text(raw_text)
    started = time.monotonic()

    try:
        provider = get_summarisation_provider()
        result: SummarisationResult = provider.summarise(cleaned)
    except Exception as exc:
        record_ai_audit(
            action=AIAuditAction.SUMMARISATION_REQUEST,
            user=user,
            student=student,
            input_text=cleaned,
            output_text=f"Provider error: {redact_text(str(exc), max_length=500)}",
            provider=CopilotProvider.SYSTEM,
            model_name="provider-error",
            metadata={"error": True},
        )
        raise serializers.ValidationError({"detail": "Summarisation service is temporarily unavailable."}) from exc

    latency_ms = result.latency_ms or int((time.monotonic() - started) * 1000)
    ai_output = {
        "key_issues": result.key_issues,
        "recommended_actions": result.recommended_actions,
        "urgency_level": result.urgency_level,
    }

    summarisation = SummarisationRequest.objects.create(
        user=user,
        student=student,
        raw_input_text=cleaned,
        ai_output=ai_output,
        status=SummarisationStatus.PENDING,
        provider=result.provider,
        model_name=result.model_name,
        latency_ms=latency_ms,
    )

    record_ai_audit(
        action=AIAuditAction.SUMMARISATION_REQUEST,
        user=user,
        student=student,
        input_text=cleaned,
        output_text=json.dumps(ai_output),
        provider=result.provider,
        model_name=result.model_name,
        metadata={
            "summarisationId": str(summarisation.id),
            "latencyMs": latency_ms,
            **redact_metadata(result.metadata),
        },
    )
    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action="SUMMARISATION_REQUEST",
        summary="Staff summarisation request processed.",
        target_type="SummarisationRequest",
        target_id=str(summarisation.id),
        severity=AuditSeverity.INFO,
        metadata={
            "summarisationId": str(summarisation.id),
            "provider": result.provider,
            "studentId": str(student.id) if student else None,
        },
        request=request,
    )
    return summarisation


@transaction.atomic
def approve_summarisation(
    *,
    user,
    summarisation: SummarisationRequest,
    human_edited_output: dict[str, Any],
    request=None,
) -> SummarisationRequest:
    if summarisation.status != SummarisationStatus.PENDING:
        raise serializers.ValidationError({"detail": "This summarisation has already been processed."})

    summarisation.human_edited_output = human_edited_output
    summarisation.status = SummarisationStatus.APPROVED
    summarisation.approved_at = timezone.now()

    if summarisation.student:
        note_text = _format_note_text(human_edited_output)
        note = AdvisingNote.objects.create(
            student=summarisation.student,
            created_by_user=user,
            note_text=note_text,
            status=AdvisingNoteStatus.APPROVED,
            approved_by_user=user,
            approved_at=timezone.now(),
        )
        summarisation.advising_note = note

    summarisation.save()

    record_ai_audit(
        action=AIAuditAction.SUMMARISATION_APPROVED,
        user=user,
        student=summarisation.student,
        input_text=summarisation.raw_input_text,
        output_text=json.dumps(summarisation.ai_output),
        provider=summarisation.provider,
        model_name=summarisation.model_name,
        metadata={
            "summarisationId": str(summarisation.id),
            "humanEditedOutput": human_edited_output,
            "advisingNoteId": str(summarisation.advising_note_id) if summarisation.advising_note_id else None,
            "approvedBy": str(user.id),
        },
    )
    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action="SUMMARISATION_APPROVED",
        summary="Staff summarisation approved and saved as official record.",
        target_type="SummarisationRequest",
        target_id=str(summarisation.id),
        severity=AuditSeverity.INFO,
        metadata={
            "summarisationId": str(summarisation.id),
            "advisingNoteId": str(summarisation.advising_note_id) if summarisation.advising_note_id else None,
            "studentId": str(summarisation.student_id) if summarisation.student_id else None,
        },
        request=request,
    )
    return summarisation


def _format_note_text(output: dict[str, Any]) -> str:
    lines = []
    urgency = output.get("urgency_level", "Routine")
    lines.append(f"Urgency: {urgency}")
    lines.append("")
    lines.append("Key Issues:")
    for issue in output.get("key_issues", []):
        lines.append(f"- {issue}")
    lines.append("")
    lines.append("Recommended Actions:")
    for action in output.get("recommended_actions", []):
        lines.append(f"- {action}")
    return "\n".join(lines)
