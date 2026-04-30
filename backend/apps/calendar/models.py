from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AcademicCalendarEventType(models.TextChoices):
    REGISTRATION_OPEN = "REGISTRATION_OPEN", "Registration Open"
    REGISTRATION_DEADLINE = "REGISTRATION_DEADLINE", "Registration Deadline"
    DROP_DEADLINE = "DROP_DEADLINE", "Drop Deadline"
    EXAM_PERIOD = "EXAM_PERIOD", "Exam Period"
    GRADE_SUBMISSION_DEADLINE = "GRADE_SUBMISSION_DEADLINE", "Grade Submission Deadline"
    TERM_START = "TERM_START", "Term Start"
    TERM_END = "TERM_END", "Term End"
    MOODLE_ACTIVITY = "MOODLE_ACTIVITY", "Moodle Activity"
    ADVISING = "ADVISING", "Advising"
    GENERAL = "GENERAL", "General"


class AcademicCalendarAudience(models.TextChoices):
    ALL = "ALL", "All"
    STUDENTS = "STUDENTS", "Students"
    FACULTY = "FACULTY", "Faculty"
    ADVISORS = "ADVISORS", "Advisors"
    ADMINS = "ADMINS", "Admins"


class AcademicCalendarPriority(models.TextChoices):
    LOW = "LOW", "Low"
    NORMAL = "NORMAL", "Normal"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class AcademicCalendarSource(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    COURSE_SECTION = "COURSE_SECTION", "Course Section"
    SYSTEM = "SYSTEM", "System"
    MOODLE = "MOODLE", "Moodle"


class AcademicCalendarStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CANCELLED = "CANCELLED", "Cancelled"
    DRAFT = "DRAFT", "Draft"


class AcademicCalendarEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=40, choices=AcademicCalendarEventType.choices)
    audience = models.CharField(max_length=16, choices=AcademicCalendarAudience.choices, default=AcademicCalendarAudience.ALL)
    priority = models.CharField(max_length=16, choices=AcademicCalendarPriority.choices, default=AcademicCalendarPriority.NORMAL)
    academic_year = models.CharField(max_length=32)
    semester = models.CharField(max_length=64)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=160, blank=True)
    related_course_section = models.ForeignKey(
        "academics.CourseSection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="academic_calendar_events",
    )
    source = models.CharField(max_length=24, choices=AcademicCalendarSource.choices, default=AcademicCalendarSource.MANUAL)
    status = models.CharField(max_length=16, choices=AcademicCalendarStatus.choices, default=AcademicCalendarStatus.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_academic_calendar_events",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at", "title", "id"]
        indexes = [
            models.Index(fields=["start_at"], name="calendar_start_idx"),
            models.Index(fields=["event_type", "start_at"], name="calendar_type_start_idx"),
            models.Index(fields=["audience", "status", "start_at"], name="calendar_aud_stat_start_idx"),
            models.Index(fields=["academic_year", "semester"], name="calendar_year_sem_idx"),
            models.Index(fields=["source", "related_course_section", "event_type"], name="calendar_source_section_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "related_course_section", "event_type"],
                name="calendar_unique_source_section_type",
            )
        ]

    def clean(self):
        super().clean()
        if not self.title.strip():
            raise ValidationError({"title": "Title is required."})
        if not self.academic_year.strip():
            raise ValidationError({"academic_year": "Academic year is required."})
        if not self.semester.strip():
            raise ValidationError({"semester": "Semester is required."})
        if self.end_at is not None and self.end_at < self.start_at:
            raise ValidationError({"end_at": "End date must be after the start date."})

    def save(self, *args, **kwargs):
        from apps.audit.services import sanitize_audit_metadata

        self.title = self.title.strip()
        self.academic_year = self.academic_year.strip()
        self.semester = self.semester.strip()
        self.metadata = sanitize_audit_metadata(self.metadata)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.academic_year} {self.semester})"
