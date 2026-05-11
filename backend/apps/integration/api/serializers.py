from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)


MAX_ERROR_LENGTH = 240


def _redact_known_secrets(value: str) -> str:
    redacted = value or ""
    secret_values = [
        getattr(settings, "MOODLE_WS_TOKEN", ""),
        getattr(settings, "LTI_PRIVATE_KEY", ""),
        getattr(settings, "LTI_PLATFORM_PUBLIC_KEY", ""),
    ]
    for secret in secret_values:
        if secret:
            redacted = redacted.replace(secret, "[redacted]")
    return redacted


def _safe_error(value: str) -> str:
    redacted = _redact_known_secrets(value)
    if len(redacted) <= MAX_ERROR_LENGTH:
        return redacted
    return f"{redacted[:MAX_ERROR_LENGTH - 3]}..."


def summarize_outbox_payload(payload: dict) -> dict:
    safe_payload = payload or {}
    return {
        "userId": safe_payload.get("user_id"),
        "sectionId": safe_payload.get("section_id"),
        "enrollmentId": safe_payload.get("enrollment_id"),
        "studentId": safe_payload.get("student_id"),
        "gradeId": safe_payload.get("grade_id"),
        "action": safe_payload.get("action") or "",
    }


class MoodleOutboxEventSerializer(serializers.ModelSerializer):
    eventType = serializers.CharField(source="event_type")
    payloadSummary = serializers.SerializerMethodField()
    lastError = serializers.SerializerMethodField()
    lastAttemptAt = serializers.DateTimeField(source="last_attempt_at", allow_null=True)
    processedAt = serializers.DateTimeField(source="processed_at", allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at")
    canRetry = serializers.SerializerMethodField()

    class Meta:
        model = IntegrationOutboxEvent
        fields = [
            "id",
            "eventType",
            "status",
            "payloadSummary",
            "attempts",
            "lastError",
            "lastAttemptAt",
            "processedAt",
            "createdAt",
            "canRetry",
        ]

    def get_payloadSummary(self, obj: IntegrationOutboxEvent) -> dict:
        return summarize_outbox_payload(obj.payload)

    def get_lastError(self, obj: IntegrationOutboxEvent) -> str:
        return _safe_error(obj.last_error)

    def get_canRetry(self, obj: IntegrationOutboxEvent) -> bool:
        return obj.status in {IntegrationEventStatus.FAILED, IntegrationEventStatus.PENDING}


class MoodleUserMapSerializer(serializers.ModelSerializer):
    sisUser = serializers.SerializerMethodField()
    sisUserId = serializers.IntegerField(source="user_id")
    moodleUserId = serializers.IntegerField(source="moodle_user_id")
    moodleUsername = serializers.CharField(source="moodle_username")
    lastSyncedAt = serializers.DateTimeField(source="last_synced_at")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = MoodleUserMap
        fields = [
            "id",
            "sisUser",
            "sisUserId",
            "moodleUserId",
            "moodleUsername",
            "lastSyncedAt",
            "createdAt",
        ]

    def get_sisUser(self, obj: MoodleUserMap) -> dict:
        return {
            "id": obj.user_id,
            "username": obj.user.username,
            "fullName": obj.user.full_name,
            "email": obj.user.email,
        }


class MoodleCourseMapSerializer(serializers.ModelSerializer):
    sisSection = serializers.SerializerMethodField()
    sectionId = serializers.UUIDField(source="section_id")
    moodleCourseId = serializers.IntegerField(source="moodle_course_id")
    moodleShortname = serializers.CharField(source="moodle_shortname")
    moodleCategoryId = serializers.IntegerField(source="moodle_category_id")
    gradeTargetConfigured = serializers.SerializerMethodField()
    gradeComponent = serializers.CharField(source="grade_component")
    gradeActivityId = serializers.IntegerField(source="grade_activity_id", allow_null=True)
    gradeItemNumber = serializers.IntegerField(source="grade_item_number", allow_null=True)
    gradeItemLabel = serializers.CharField(source="grade_item_label")
    lastSyncedAt = serializers.DateTimeField(source="last_synced_at")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = MoodleCourseMap
        fields = [
            "id",
            "sisSection",
            "sectionId",
            "moodleCourseId",
            "moodleShortname",
            "moodleCategoryId",
            "gradeTargetConfigured",
            "gradeComponent",
            "gradeActivityId",
            "gradeItemNumber",
            "gradeItemLabel",
            "lastSyncedAt",
            "createdAt",
        ]

    def get_sisSection(self, obj: MoodleCourseMap) -> dict:
        section = obj.section
        return {
            "id": str(section.id),
            "courseCode": section.course.course_code,
            "courseTitle": section.course.course_title,
            "sectionCode": section.section_code,
        }

    def get_gradeTargetConfigured(self, obj: MoodleCourseMap) -> bool:
        return bool(
            obj.grade_component
            and obj.grade_activity_id is not None
            and obj.grade_item_number is not None
        )


class MoodleEngagementRunSerializer(serializers.ModelSerializer):
    dryRun = serializers.BooleanField(source="dry_run")
    startedAt = serializers.DateTimeField(source="started_at")
    completedAt = serializers.DateTimeField(source="completed_at", allow_null=True)
    coursesInspected = serializers.IntegerField(source="courses_inspected")
    usersInspected = serializers.IntegerField(source="users_inspected")
    snapshotsCreated = serializers.IntegerField(source="snapshots_created")
    snapshotsUpdated = serializers.IntegerField(source="snapshots_updated")
    snapshotsTotal = serializers.SerializerMethodField()
    skippedUnmappedUsers = serializers.IntegerField(source="skipped_unmapped_users")
    failureCount = serializers.IntegerField(source="failure_count")
    lastError = serializers.SerializerMethodField()

    class Meta:
        model = MoodleEngagementIngestionRun
        fields = [
            "id",
            "status",
            "dryRun",
            "startedAt",
            "completedAt",
            "coursesInspected",
            "usersInspected",
            "snapshotsCreated",
            "snapshotsUpdated",
            "snapshotsTotal",
            "skippedUnmappedUsers",
            "failureCount",
            "lastError",
        ]

    def get_snapshotsTotal(self, obj: MoodleEngagementIngestionRun) -> int:
        return obj.snapshots_created + obj.snapshots_updated

    def get_lastError(self, obj: MoodleEngagementIngestionRun) -> str:
        return _safe_error(obj.last_error)


class MoodleEngagementSnapshotSerializer(serializers.ModelSerializer):
    studentUser = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    moodleUserId = serializers.IntegerField(source="moodle_user_id")
    moodleCourseId = serializers.IntegerField(source="moodle_course_id")
    moodleLastAccessAt = serializers.DateTimeField(source="moodle_last_access_at", allow_null=True)
    moodleCourseLastAccessAt = serializers.DateTimeField(source="moodle_course_last_access_at", allow_null=True)
    assignmentSubmissionCount = serializers.IntegerField(source="assignment_submission_count", allow_null=True)
    assignmentSubmissionRate = serializers.DecimalField(
        source="assignment_submission_rate",
        max_digits=5,
        decimal_places=2,
        allow_null=True,
    )
    quizAttemptCount = serializers.IntegerField(source="quiz_attempt_count", allow_null=True)
    quizAverage = serializers.DecimalField(source="quiz_average", max_digits=5, decimal_places=2, allow_null=True)
    forumPostCount = serializers.IntegerField(source="forum_post_count", allow_null=True)
    collectedAt = serializers.DateTimeField(source="collected_at")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = MoodleEngagementSnapshot
        fields = [
            "id",
            "studentUser",
            "student",
            "section",
            "moodleUserId",
            "moodleCourseId",
            "moodleLastAccessAt",
            "moodleCourseLastAccessAt",
            "assignmentSubmissionCount",
            "assignmentSubmissionRate",
            "quizAttemptCount",
            "quizAverage",
            "forumPostCount",
            "collectedAt",
            "createdAt",
        ]

    def get_studentUser(self, obj: MoodleEngagementSnapshot) -> dict | None:
        if obj.user is None:
            return None
        return {
            "id": obj.user_id,
            "username": obj.user.username,
            "fullName": obj.user.full_name,
            "email": obj.user.email,
        }

    def get_student(self, obj: MoodleEngagementSnapshot) -> dict | None:
        if obj.student is None:
            return None
        return {
            "id": str(obj.student_id),
            "studentNumber": obj.student.student_number,
        }

    def get_section(self, obj: MoodleEngagementSnapshot) -> dict | None:
        if obj.section is None:
            return None
        return {
            "id": str(obj.section_id),
            "courseCode": obj.section.course.course_code,
            "courseTitle": obj.section.course.course_title,
            "sectionCode": obj.section.section_code,
        }
