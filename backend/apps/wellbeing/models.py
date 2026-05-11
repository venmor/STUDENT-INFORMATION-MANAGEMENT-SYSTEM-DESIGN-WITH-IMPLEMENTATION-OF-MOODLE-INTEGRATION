from __future__ import annotations

import uuid

from django.db import models


class TriageClass(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    CONCERNING = "CONCERNING", "Concerning"
    ESCALATE = "ESCALATE", "Escalate"


class WellbeingConsent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="wellbeing_consent",
    )
    is_enabled = models.BooleanField(default=False)
    consented_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.student_id}:{self.is_enabled}"


class WellbeingCheckIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="wellbeing_checkins",
    )
    mood_rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    triage_class = models.CharField(
        max_length=12,
        choices=TriageClass.choices,
        default=TriageClass.NORMAL,
    )
    is_deleted_by_student = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "-created_at"], name="wb_student_idx"),
            models.Index(fields=["triage_class", "-created_at"], name="wb_triage_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.student_id}:{self.mood_rating}:{self.triage_class}"


class WellbeingAuditLog(models.Model):
    """Minimal safeguarding metadata only. No free-text."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="wellbeing_audit_logs",
    )
    checkin_id = models.UUIDField(null=True, blank=True)
    triage_class = models.CharField(max_length=12, choices=TriageClass.choices)
    notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.student_id}:{self.triage_class}:{self.created_at}"
