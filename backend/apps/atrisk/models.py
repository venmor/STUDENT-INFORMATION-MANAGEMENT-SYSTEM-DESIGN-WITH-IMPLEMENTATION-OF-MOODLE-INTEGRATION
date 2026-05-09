from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AlertSeverity(models.TextChoices):
    HIGH = "HIGH", "High"
    MEDIUM = "MEDIUM", "Medium"
    LOW = "LOW", "Low"


class AtRiskAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="at_risk_alerts",
    )
    severity = models.CharField(max_length=8, choices=AlertSeverity.choices)
    active_signals = models.JSONField(default=list)
    explanation = models.TextField()
    provider = models.CharField(max_length=40, default="deterministic")
    model_name = models.CharField(max_length=120, blank=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_at_risk_alerts",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-severity", "-created_at"]
        indexes = [
            models.Index(fields=["student", "-created_at"], name="atrisk_student_idx"),
            models.Index(fields=["severity", "-created_at"], name="atrisk_severity_idx"),
            models.Index(fields=["is_acknowledged", "-created_at"], name="atrisk_ack_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.student_id}:{self.severity}:{self.id}"
