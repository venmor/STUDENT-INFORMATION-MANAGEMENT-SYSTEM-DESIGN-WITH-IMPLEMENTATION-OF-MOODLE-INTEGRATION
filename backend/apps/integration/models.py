from __future__ import annotations

import uuid

from django.db import models


class IntegrationEventStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSED = "PROCESSED", "Processed"
    FAILED = "FAILED", "Failed"


class IntegrationOutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=16,
        choices=IntegrationEventStatus.choices,
        default=IntegrationEventStatus.PENDING,
    )
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.status}"


class MoodleUserMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "accounts.User", on_delete=models.CASCADE, related_name="moodle_user_map"
    )
    moodle_user_id = models.PositiveIntegerField(unique=True)
    moodle_username = models.CharField(max_length=150)
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user_id"]

    def __str__(self) -> str:
        return f"{self.user.username}:{self.moodle_user_id}"


class MoodleCourseMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.OneToOneField(
        "academics.CourseSection",
        on_delete=models.CASCADE,
        related_name="moodle_course_map",
    )
    moodle_course_id = models.PositiveIntegerField(unique=True)
    moodle_shortname = models.CharField(max_length=255)
    moodle_category_id = models.PositiveIntegerField()
    grade_component = models.CharField(max_length=64, blank=True)
    grade_activity_id = models.PositiveIntegerField(null=True, blank=True)
    grade_item_number = models.PositiveIntegerField(null=True, blank=True)
    grade_item_label = models.CharField(max_length=255, blank=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["section_id"]

    def __str__(self) -> str:
        return f"{self.section_id}:{self.moodle_course_id}"


class MoodleEngagementIngestionStatus(models.TextChoices):
    RUNNING = "RUNNING", "Running"
    SUCCEEDED = "SUCCEEDED", "Succeeded"
    PARTIAL = "PARTIAL", "Partial"
    FAILED = "FAILED", "Failed"
    DRY_RUN = "DRY_RUN", "Dry run"


class MoodleEngagementIngestionRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=16,
        choices=MoodleEngagementIngestionStatus.choices,
        default=MoodleEngagementIngestionStatus.RUNNING,
    )
    dry_run = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    courses_inspected = models.PositiveIntegerField(default=0)
    users_inspected = models.PositiveIntegerField(default=0)
    snapshots_created = models.PositiveIntegerField(default=0)
    snapshots_updated = models.PositiveIntegerField(default=0)
    skipped_unmapped_users = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    summary_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at", "id"]

    def __str__(self) -> str:
        return f"moodle-engagement:{self.status}:{self.started_at:%Y-%m-%d %H:%M:%S}"


class MoodleEngagementSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        MoodleEngagementIngestionRun,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    user = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moodle_engagement_snapshots",
    )
    student = models.ForeignKey(
        "students.StudentProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moodle_engagement_snapshots",
    )
    section = models.ForeignKey(
        "academics.CourseSection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moodle_engagement_snapshots",
    )
    moodle_user_id = models.PositiveIntegerField()
    moodle_course_id = models.PositiveIntegerField()
    moodle_last_access_at = models.DateTimeField(null=True, blank=True)
    moodle_course_last_access_at = models.DateTimeField(null=True, blank=True)
    assignment_submission_count = models.PositiveIntegerField(null=True, blank=True)
    assignment_submission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    quiz_attempt_count = models.PositiveIntegerField(null=True, blank=True)
    quiz_average = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    forum_post_count = models.PositiveIntegerField(null=True, blank=True)
    raw_summary = models.JSONField(default=dict, blank=True)
    collected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-collected_at", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["run", "moodle_user_id", "moodle_course_id"],
                name="unique_moodle_engagement_snapshot_per_run_user_course",
            )
        ]
        indexes = [
            models.Index(fields=["moodle_user_id", "moodle_course_id"]),
            models.Index(fields=["section", "collected_at"]),
            models.Index(fields=["student", "collected_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.moodle_course_id}:{self.moodle_user_id}:{self.collected_at:%Y-%m-%d %H:%M:%S}"


class LtiOidcState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=160, unique=True)
    nonce = models.CharField(max_length=160, unique=True)
    issuer = models.URLField(max_length=500)
    client_id = models.CharField(max_length=255)
    deployment_id = models.CharField(max_length=255, blank=True)
    login_hint = models.CharField(max_length=500)
    lti_message_hint = models.CharField(max_length=500, blank=True)
    target_link_uri = models.URLField(max_length=1000)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["state", "expires_at"]),
            models.Index(fields=["nonce", "expires_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.issuer}:{self.client_id}:{self.state}"


class LtiLaunchSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_token_hash = models.CharField(max_length=64, unique=True)
    issuer = models.URLField(max_length=500)
    client_id = models.CharField(max_length=255)
    deployment_id = models.CharField(max_length=255)
    tool_slug = models.CharField(max_length=64)
    moodle_subject = models.CharField(max_length=255)
    moodle_user_id = models.CharField(max_length=64, blank=True)
    moodle_course_id = models.CharField(max_length=64, blank=True)
    moodle_roles = models.JSONField(default=list, blank=True)
    launch_claims = models.JSONField(default=dict, blank=True)
    user = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lti_launch_sessions",
    )
    section = models.ForeignKey(
        "academics.CourseSection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lti_launch_sessions",
    )
    expires_at = models.DateTimeField()
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session_token_hash", "expires_at"]),
            models.Index(fields=["tool_slug", "expires_at"]),
            models.Index(fields=["moodle_user_id"]),
            models.Index(fields=["moodle_course_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.tool_slug}:{self.issuer}:{self.moodle_subject}"
