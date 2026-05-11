from __future__ import annotations

import json
import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely
from apps.copilot.audit import record_ai_audit
from apps.copilot.models import AIAuditAction, CopilotProvider
from apps.students.models import StudentProfile

from .config import SIGNAL_THRESHOLDS
from .models import AlertSeverity, AtRiskAlert
from .signals import evaluate_all_signals


logger = logging.getLogger(__name__)


def evaluate_student_signals(student: StudentProfile) -> list[str]:
    """Evaluate all signals for a student, return list of active signal names."""
    results = evaluate_all_signals(student)
    return [name for name, is_active in results.items() if is_active]


def classify_severity(active_signals: list[str]) -> str | None:
    """
    Classify alert severity based on active signals.

    Rules (SRS):
    - HIGH: Any 1 High-weight signal active, OR any 3+ signals active of any weight
    - MEDIUM: Any 2 Medium-weight signals active, OR 1 Medium + 2 Low signals
    - LOW: Any 1 Low or 1 Medium signal active in isolation
    - None: No signals active
    """
    if not active_signals:
        return None

    weights = [SIGNAL_THRESHOLDS[s]["weight"] for s in active_signals if s in SIGNAL_THRESHOLDS]
    high_count = weights.count("HIGH")
    medium_count = weights.count("MEDIUM")
    low_count = weights.count("LOW")
    total = len(weights)

    if total == 0:
        return None
    if high_count >= 1 or total >= 3:
        return AlertSeverity.HIGH
    if medium_count >= 2 or (medium_count >= 1 and low_count >= 2):
        return AlertSeverity.MEDIUM
    return AlertSeverity.LOW


def generate_explanation(student: StudentProfile, active_signals: list[str], severity: str) -> str:
    """Build a deterministic explanation for an at-risk alert."""
    signal_descriptions = {
        "attendance_flag": "attendance has dropped below 75%",
        "academic_probation": "is currently on academic probation",
        "financial_hold": "has an active financial hold on their record",
        "grade_decline": "has experienced a GPA decline of 0.5 or more",
        "incomplete_grade": "has 2 or more incomplete grades this semester",
        "moodle_inactivity": "has not logged into Moodle for 14 or more days",
        "assignment_miss_rate": "has missed 2 or more assignment deadlines",
        "quiz_failure_pattern": "has an average quiz score below 40%",
        "forum_disengagement": "has zero forum participation for 21 or more days",
    }

    student_label = f"Student {student.student_number}"
    descriptions = [signal_descriptions.get(s, s) for s in active_signals]

    if severity == AlertSeverity.HIGH:
        intro = f"{student_label} requires immediate attention."
    elif severity == AlertSeverity.MEDIUM:
        intro = f"{student_label} shows concerning patterns that warrant follow-up."
    else:
        intro = f"{student_label} has a minor concern to monitor."

    if len(descriptions) == 1:
        detail = f"The student {descriptions[0]}."
    elif len(descriptions) == 2:
        detail = f"The student {descriptions[0]} and {descriptions[1]}."
    else:
        listed = ", ".join(descriptions[:-1]) + f", and {descriptions[-1]}"
        detail = f"The student {listed}."

    action = "Advisor review and intervention is recommended."
    return f"{intro} {detail} {action}"


@transaction.atomic
def process_student(student: StudentProfile) -> AtRiskAlert | None:
    """Evaluate signals for a single student, create/update/close alert as appropriate."""
    active_signals = evaluate_student_signals(student)
    severity = classify_severity(active_signals)

    open_alert = AtRiskAlert.objects.filter(
        student=student, is_closed=False, is_acknowledged=False
    ).first()

    if severity is None:
        if open_alert:
            open_alert.is_closed = True
            open_alert.closed_at = timezone.now()
            open_alert.save(update_fields=["is_closed", "closed_at", "updated_at"])
        return None

    if open_alert:
        open_alert.severity = severity
        open_alert.active_signals = active_signals
        open_alert.explanation = generate_explanation(student, active_signals, severity)
        open_alert.save(update_fields=["severity", "active_signals", "explanation", "updated_at"])
        return open_alert

    alert = AtRiskAlert.objects.create(
        student=student,
        severity=severity,
        active_signals=active_signals,
        explanation=generate_explanation(student, active_signals, severity),
        provider="deterministic",
        model_name="deterministic-at-risk-v1",
    )
    return alert


def run_at_risk_engine(*, request=None) -> dict[str, Any]:
    """Process all active students. Returns summary stats."""
    active_students = StudentProfile.objects.filter(is_active=True)
    results: dict[str, Any] = {
        "students_processed": 0,
        "alerts_created": 0,
        "alerts_updated": 0,
        "alerts_closed": 0,
        "errors": 0,
    }

    for student in active_students:
        try:
            existing_open = AtRiskAlert.objects.filter(
                student=student, is_closed=False, is_acknowledged=False
            ).first()
            alert = process_student(student)
            results["students_processed"] += 1

            if alert and not existing_open:
                results["alerts_created"] += 1
                record_ai_audit(
                    action=AIAuditAction.AT_RISK_EVALUATION,
                    user=None,
                    student=student,
                    input_text=json.dumps(alert.active_signals),
                    output_text=alert.explanation,
                    provider=CopilotProvider.DETERMINISTIC,
                    model_name=alert.model_name,
                    metadata={
                        "alertId": str(alert.id),
                        "severity": alert.severity,
                        "signals": alert.active_signals,
                        "feature": "at_risk_engine",
                    },
                )
            elif alert and existing_open:
                results["alerts_updated"] += 1
            elif not alert and existing_open:
                results["alerts_closed"] += 1
        except Exception:
            results["errors"] += 1
            logger.exception("At-risk engine error for student %s", student.id)

    record_audit_event_safely(
        actor=None,
        category=AuditCategory.AI,
        action="AT_RISK_ENGINE_RUN",
        summary=(
            f"At-risk engine completed: {results['students_processed']} students processed, "
            f"{results['alerts_created']} alerts created."
        ),
        target_type="AtRiskEngine",
        target_id="nightly-run",
        severity=AuditSeverity.INFO,
        metadata=results,
        request=request,
    )
    return results


@transaction.atomic
def acknowledge_alert(*, user, alert_id=None, alert: AtRiskAlert | None = None) -> AtRiskAlert:
    """Acknowledge an open alert."""
    if alert is None:
        alert = AtRiskAlert.objects.select_for_update().get(
            id=alert_id, is_acknowledged=False, is_closed=False
        )
    alert.is_acknowledged = True
    alert.acknowledged_by = user
    alert.acknowledged_at = timezone.now()
    alert.save(update_fields=["is_acknowledged", "acknowledged_by", "acknowledged_at", "updated_at"])
    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action="AT_RISK_ALERT_ACKNOWLEDGED",
        summary=f"At-risk alert acknowledged for student {alert.student.student_number}.",
        target_type="AtRiskAlert",
        target_id=str(alert.id),
        severity=AuditSeverity.INFO,
        metadata={"severity": alert.severity, "signals": alert.active_signals},
    )
    return alert


def auto_close_resolved_alerts() -> int:
    """Auto-close alerts where signals have resolved. Returns count of closed alerts."""
    open_alerts = AtRiskAlert.objects.filter(
        is_closed=False, is_acknowledged=False
    ).select_related("student")
    closed_count = 0

    for alert in open_alerts:
        active_signals = evaluate_student_signals(alert.student)
        severity = classify_severity(active_signals)
        if severity is None:
            alert.is_closed = True
            alert.closed_at = timezone.now()
            alert.save(update_fields=["is_closed", "closed_at", "updated_at"])
            closed_count += 1

    return closed_count
