from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class SummarisationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    DISCARDED = "DISCARDED", "Discarded"


class UrgencyLevel(models.TextChoices):
    ROUTINE = "Routine", "Routine"
    FOLLOW_UP_NEEDED = "Follow-up Needed", "Follow-up Needed"
    URGENT = "Urgent", "Urgent"


class SummarisationRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summarisation_requests",
    )
    student = models.ForeignKey(
        "students.StudentProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="summarisation_requests",
    )
    raw_input_text = models.TextField()
    ai_output = models.JSONField(default=dict)
    human_edited_output = models.JSONField(null=True, blank=True)
    advising_note = models.ForeignKey(
        "students.AdvisingNote",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="summarisation_requests",
    )
    status = models.CharField(
        max_length=16,
        choices=SummarisationStatus.choices,
        default=SummarisationStatus.PENDING,
    )
    provider = models.CharField(max_length=40)
    model_name = models.CharField(max_length=120, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="summ_user_idx"),
            models.Index(fields=["student", "-created_at"], name="summ_student_idx"),
            models.Index(fields=["status", "-created_at"], name="summ_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.status}:{self.id}"
