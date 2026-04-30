from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AuditCategory(models.TextChoices):
    USER = "USER", "User"
    STUDENT_RECORD = "STUDENT_RECORD", "Student Record"
    COURSE = "COURSE", "Course"
    ENROLLMENT = "ENROLLMENT", "Enrollment"
    GRADE = "GRADE", "Grade"
    MOODLE = "MOODLE", "Moodle"
    NOTIFICATION = "NOTIFICATION", "Notification"
    ACADEMIC_CALENDAR = "ACADEMIC_CALENDAR", "Academic Calendar"
    LTI = "LTI", "LTI"
    SYSTEM = "SYSTEM", "System"
    AI = "AI", "AI"


class AuditSeverity(models.TextChoices):
    INFO = "INFO", "Info"
    SUCCESS = "SUCCESS", "Success"
    WARNING = "WARNING", "Warning"
    ERROR = "ERROR", "Error"


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    actor_username = models.CharField(max_length=150, blank=True)
    actor_role = models.CharField(max_length=32, blank=True)
    category = models.CharField(max_length=32, choices=AuditCategory.choices, db_index=True)
    action = models.CharField(max_length=80, db_index=True)
    summary = models.TextField()
    target_type = models.CharField(max_length=128, blank=True)
    target_id = models.CharField(max_length=128, blank=True)
    severity = models.CharField(max_length=16, choices=AuditSeverity.choices, default=AuditSeverity.INFO, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["created_at"], name="audit_created_idx"),
            models.Index(fields=["category", "created_at"], name="audit_cat_created_idx"),
            models.Index(fields=["severity", "created_at"], name="audit_sev_created_idx"),
            models.Index(fields=["action", "created_at"], name="audit_action_created_idx"),
            models.Index(fields=["actor", "created_at"], name="audit_actor_created_idx"),
            models.Index(fields=["target_type", "target_id"], name="audit_target_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.category}:{self.action}:{self.id}"
