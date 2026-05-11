from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class NotificationCategory(models.TextChoices):
    ACADEMIC = "ACADEMIC", "Academic"
    MOODLE = "MOODLE", "Moodle"
    GRADES = "GRADES", "Grades"
    ENROLLMENT = "ENROLLMENT", "Enrollment"
    ADVISING = "ADVISING", "Advising"
    SYSTEM = "SYSTEM", "System"


class NotificationSeverity(models.TextChoices):
    INFO = "INFO", "Info"
    SUCCESS = "SUCCESS", "Success"
    WARNING = "WARNING", "Warning"
    ERROR = "ERROR", "Error"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    category = models.CharField(max_length=16, choices=NotificationCategory.choices)
    severity = models.CharField(max_length=16, choices=NotificationSeverity.choices)
    title = models.CharField(max_length=160)
    message = models.TextField()
    action_label = models.CharField(max_length=80, blank=True)
    action_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    source_type = models.CharField(max_length=128, blank=True)
    source_id = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"], name="notif_rec_read_idx"),
            models.Index(fields=["recipient", "category", "-created_at"], name="notifications_category_idx"),
            models.Index(fields=["recipient", "severity", "-created_at"], name="notifications_severity_idx"),
            models.Index(fields=["source_type", "source_id"], name="notifications_source_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.recipient_id}:{self.category}:{self.title}"
