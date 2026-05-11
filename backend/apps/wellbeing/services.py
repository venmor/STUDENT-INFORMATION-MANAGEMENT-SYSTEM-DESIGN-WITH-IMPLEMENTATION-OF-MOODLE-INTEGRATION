from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.notifications.services import create_notification
from apps.accounts.models import User
from apps.students.models import StudentProfile
from apps.copilot.providers import get_copilot_provider

from .models import TriageClass, WellbeingAuditLog, WellbeingCheckIn, WellbeingConsent
from .prompts import WELLBEING_SUPPORT_PROMPT


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
) -> dict[str, Any]:
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

    # AI-WBE-003: LLM for supportive wording if not escalation
    supportive_text = ""
    if triage != TriageClass.ESCALATE:
        supportive_text = generate_supportive_text(mood_rating, comment)

    return {
        "id": checkin.id,
        "mood_rating": checkin.mood_rating,
        "triage_class": checkin.triage_class,
        "created_at": checkin.created_at,
        "supportive_text": supportive_text,
    }


def generate_supportive_text(mood_rating: int, comment: str) -> str:
    """Use LLM to draft supportive wording for non-escalation outcomes."""
    mood_labels = {1: "Very difficult", 2: "Difficult", 3: "Okay", 4: "Good", 5: "Very good"}
    prompt = WELLBEING_SUPPORT_PROMPT.format(
        mood_label=mood_labels.get(mood_rating, "Unknown"),
        mood_rating=mood_rating,
        comment=comment or "No comment provided."
    )

    try:
        provider = get_copilot_provider()
        # Mock/Simple call to provider
        # Note: In deterministic mode, this returns a fixed response based on prompt match
        result = provider.generate(
            question=f"Mood check-in support: {mood_rating}",
            retrieved_chunks=[],
            safe_student_context={},
            system_prompt=prompt
        )
        return result.answer
    except Exception:
        logger.exception("Failed to generate supportive wellbeing text")
        return "Thank you for sharing how you feel."


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
            category="SYSTEM",
            severity="HIGH",
            title="IMMEDIATE: Wellbeing Escalation",
            message=f"Student {checkin.student.student_number} submitted a high-risk wellbeing check-in.",
            action_url=f"/advisor/wellbeing/alerts/{checkin.id}",
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
