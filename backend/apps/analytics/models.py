from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AnalyticsETLRunStatus(models.TextChoices):
    STARTED = "STARTED", "Started"
    SUCCEEDED = "SUCCEEDED", "Succeeded"
    FAILED = "FAILED", "Failed"
    PARTIAL = "PARTIAL", "Partial"


class AnalyticsETLRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=16, choices=AnalyticsETLRunStatus.choices, default=AnalyticsETLRunStatus.STARTED)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    students_processed = models.PositiveIntegerField(default=0)
    snapshots_created = models.PositiveIntegerField(default=0)
    snapshots_updated = models.PositiveIntegerField(default=0)
    moodle_snapshots_used = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    dry_run = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at", "id"]

    def __str__(self) -> str:
        return f"analytics-etl:{self.status}:{self.started_at:%Y-%m-%d %H:%M:%S}"


class StudentAnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="analytics_snapshots")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="student_analytics_snapshots")
    academic_year = models.CharField(max_length=32)
    semester = models.CharField(max_length=64)
    programme = models.CharField(max_length=128)
    year_of_study = models.PositiveSmallIntegerField()
    academic_standing = models.CharField(max_length=32)
    attendance_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    financial_flag_count = models.PositiveIntegerField(default=0)
    active_enrollment_count = models.PositiveIntegerField(default=0)
    draft_grade_count = models.PositiveIntegerField(default=0)
    official_grade_count = models.PositiveIntegerField(default=0)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    latest_moodle_access_at = models.DateTimeField(null=True, blank=True)
    latest_moodle_course_access_at = models.DateTimeField(null=True, blank=True)
    moodle_snapshot_count = models.PositiveIntegerField(default=0)
    source_run = models.ForeignKey(AnalyticsETLRun, on_delete=models.PROTECT, related_name="snapshots")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student__student_number", "academic_year", "semester"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academic_year", "semester"],
                name="analytics_unique_student_snapshot_per_term",
            )
        ]
        indexes = [
            models.Index(fields=["academic_year", "semester"], name="analytics_snapshot_term_idx"),
            models.Index(fields=["programme"], name="analytics_snap_prog_idx"),
            models.Index(fields=["updated_at"], name="analytics_snapshot_updated_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.student.student_number}:{self.academic_year}:{self.semester}"
