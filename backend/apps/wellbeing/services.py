from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.notifications.services import create_notification
from apps.accounts.models import User
from apps.students.models import StudentProfile

from .models import TriageClass, WellbeingAuditLog, WellbeingCheckIn, WellbeingConsent


logger = logging.getLogger(__name__)

# Institution-approved keywords for escalation
ESCALATE_KEYWORDS = {
    "harm", "suicide", "end", "kill", "die", "death", "hurt", "self-harm",
    "emergency", "danger", "abuse", "assault", "violence", "threat"
}

CONCERNING_KEYWORDS = {
    "struggling", "depressed", "anxious", "overwhelmed", "hopeless",
    "cannot cope", "giving up", "sad", "unhappy", "lonely", "isolated"
}


def evaluate_triage(mood_rating: int, comment: str) -> TriageClass:
    """Deterministic triage rules engine (AI-WBE-003)."""
    normalized_comment = comment.lower()

    # 1. Escalate rules
    if mood_rating == 1:
        return TriageClass.ESCALATE

    for word in ESCALATE_KEYWORDS:
        if word in normalized_comment:
            return TriageClass.ESCALATE

    # 2. Concerning rules
    if mood_rating == 2:
        return TriageClass.CONCERNING

    for word in CONCERNING_KEYWORDS:
        if word in normalized_comment:
            return TriageClass.CONCERNING

    # 3. Default to Normal
    return TriageClass.NORMAL


@transaction.atomic
def process_wellbeing_checkin(
    student: StudentProfile,
    mood_rating: int,
    comment: str = "",
) -> WellbeingCheckIn:
    """Submit a new check-in and handle triage/escalation."""
    triage = evaluate_triage(mood_rating, comment)

    checkin = WellbeingCheckIn.objects.create(
        student=student,
        mood_rating=mood_rating,
        comment=comment,
        triage_class=triage,
    )

    notification_sent = False
    if triage == TriageClass.ESCALATE:
        notification_sent = notify_wellbeing_coordinators(checkin)

    # Safeguarding audit only
    WellbeingAuditLog.objects.create(
        student=student,
        checkin_id=checkin.id,
        triage_class=triage,
        notification_sent=notification_sent,
    )

    return checkin


def notify_wellbeing_coordinators(checkin: WellbeingCheckIn) -> bool:
    """Send real-time alerts to staff with wellbeing_coordinator capability."""
    coordinators = User.objects.filter(
        capabilities__capability_name="wellbeing_coordinator",
        is_active=True
    ).distinct()

    if not coordinators.exists():
        logger.warning("No wellbeing coordinators available for escalation!")
        return False

    for coordinator in coordinators:
        create_notification(
            recipient=coordinator,
            title="IMMEDIATE: Wellbeing Escalation",
            message=f"Student {checkin.student.student_number} submitted a high-risk wellbeing check-in.",
            category="SYSTEM",
            severity="HIGH",
            action_url=f"/advisor/wellbeing/alerts/{checkin.id}", # Future coordinator view
        )
    return True


@transaction.atomic
def set_wellbeing_consent(student: StudentProfile, is_enabled: bool) -> WellbeingConsent:
    """Toggle student opt-in status."""
    consent, _ = WellbeingConsent.objects.get_or_create(student=student)
    consent.is_enabled = is_enabled
    if is_enabled:
        consent.consented_at = timezone.now()
        consent.revoked_at = None
    else:
        consent.revoked_at = timezone.now()
    consent.save()
    return consent


def get_anonymized_mood_trends() -> list[dict[str, Any]]:
    """Aggregate anonymised weekly mood trends (AI-WBE-007)."""
    # Simple implementation for Wave 6: count by rating
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncWeek

    return list(
        WellbeingCheckIn.objects.filter(is_deleted_by_student=False)
        .annotate(week=TruncWeek("created_at"))
        .values("week")
        .annotate(
            avg_mood=Avg("mood_rating"),
            count=Count("id")
        )
        .order_by("-week")[:12]
    )
