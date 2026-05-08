from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class CopilotSessionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ARCHIVED = "ARCHIVED", "Archived"


class CopilotMessageRole(models.TextChoices):
    USER = "USER", "User"
    ASSISTANT = "ASSISTANT", "Assistant"
    SYSTEM = "SYSTEM", "System"


class CopilotConfidence(models.TextChoices):
    HIGH = "HIGH", "High"
    MEDIUM = "MEDIUM", "Medium"
    LOW = "LOW", "Low"
    UNSUPPORTED = "UNSUPPORTED", "Unsupported"


class CopilotProvider(models.TextChoices):
    DETERMINISTIC = "deterministic", "Deterministic"
    OPENAI_COMPATIBLE = "openai_compatible", "OpenAI compatible"
    SYSTEM = "system", "System"


class AIAuditAction(models.TextChoices):
    COPILOT_QUERY = "COPILOT_QUERY", "Co-pilot query"
    COPILOT_RESPONSE = "COPILOT_RESPONSE", "Co-pilot response"
    COPILOT_LOW_CONFIDENCE = "COPILOT_LOW_CONFIDENCE", "Co-pilot low confidence"
    COPILOT_PROVIDER_ERROR = "COPILOT_PROVIDER_ERROR", "Co-pilot provider error"
    COPILOT_RETRIEVAL_ONLY = "COPILOT_RETRIEVAL_ONLY", "Co-pilot retrieval only"
    SUMMARISATION_REQUEST = "SUMMARISATION_REQUEST", "Summarisation request"
    SUMMARISATION_APPROVED = "SUMMARISATION_APPROVED", "Summarisation approved"


class CopilotFeedbackRating(models.TextChoices):
    HELPFUL = "HELPFUL", "Helpful"
    NOT_HELPFUL = "NOT_HELPFUL", "Not helpful"


class CopilotSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="copilot_sessions")
    student = models.ForeignKey(
        "students.StudentProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copilot_sessions",
    )
    title = models.CharField(max_length=120)
    status = models.CharField(max_length=16, choices=CopilotSessionStatus.choices, default=CopilotSessionStatus.ACTIVE)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-last_message_at", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["user", "status", "-last_message_at"], name="copilot_session_user_idx"),
            models.Index(fields=["student", "status"], name="copilot_session_student_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.title}"


class CopilotMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(CopilotSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=CopilotMessageRole.choices)
    content = models.TextField()
    safe_content = models.TextField(blank=True)
    source_references = models.JSONField(default=list, blank=True)
    confidence = models.CharField(max_length=16, choices=CopilotConfidence.choices, default=CopilotConfidence.UNSUPPORTED)
    provider = models.CharField(max_length=40, choices=CopilotProvider.choices, default=CopilotProvider.SYSTEM)
    model_name = models.CharField(max_length=120, blank=True)
    retrieval_query = models.TextField(blank=True)
    retrieved_chunk_count = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["session", "created_at"], name="copilot_msg_session_idx"),
            models.Index(fields=["role", "created_at"], name="copilot_msg_role_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.session_id}:{self.role}:{self.id}"


class AIAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="ai_audit_logs")
    student = models.ForeignKey(
        "students.StudentProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_audit_logs",
    )
    session = models.ForeignKey(CopilotSession, null=True, blank=True, on_delete=models.SET_NULL, related_name="ai_audit_logs")
    message = models.ForeignKey(CopilotMessage, null=True, blank=True, on_delete=models.SET_NULL, related_name="ai_audit_logs")
    action = models.CharField(max_length=40, choices=AIAuditAction.choices, db_index=True)
    input_text = models.TextField(blank=True)
    output_text = models.TextField(blank=True)
    source_count = models.PositiveIntegerField(default=0)
    confidence = models.CharField(max_length=16, choices=CopilotConfidence.choices, default=CopilotConfidence.UNSUPPORTED)
    provider = models.CharField(max_length=40, choices=CopilotProvider.choices, default=CopilotProvider.SYSTEM)
    model_name = models.CharField(max_length=120, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_ai_audit_logs",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["action", "created_at"], name="ai_audit_action_idx"),
            models.Index(fields=["user", "created_at"], name="ai_audit_user_idx"),
            models.Index(fields=["student", "created_at"], name="ai_audit_student_idx"),
            models.Index(fields=["session", "created_at"], name="ai_audit_session_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action}:{self.id}"


class CopilotFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(CopilotMessage, on_delete=models.CASCADE, related_name="feedback")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="copilot_feedback")
    rating = models.CharField(max_length=16, choices=CopilotFeedbackRating.choices)
    comment = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["message", "user"], name="copilot_unique_feedback_per_message_user")
        ]

    def __str__(self) -> str:
        return f"{self.message_id}:{self.user_id}:{self.rating}"
