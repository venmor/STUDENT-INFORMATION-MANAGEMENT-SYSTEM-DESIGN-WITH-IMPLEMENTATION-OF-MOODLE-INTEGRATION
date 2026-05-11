from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.students.models import AcademicStanding


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_code = models.CharField(max_length=32, unique=True)
    course_title = models.CharField(max_length=255)
    department = models.CharField(max_length=128)
    credit_hours = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    programme_code = models.CharField(max_length=128, blank=True)
    max_capacity = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course_code"]


class CoursePrerequisite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="prerequisites")
    prerequisite_course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="required_for_courses",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "prerequisite_course"],
                name="academics_unique_prerequisite_pair",
            )
        ]


class CourseSectionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ARCHIVED = "ARCHIVED", "Archived"


class CourseSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="sections")
    section_code = models.CharField(max_length=32)
    faculty_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_sections",
    )
    room = models.CharField(max_length=128)
    semester = models.CharField(max_length=64)
    academic_year = models.CharField(max_length=32)
    max_capacity = models.PositiveIntegerField()
    registration_opens_at = models.DateTimeField()
    registration_closes_at = models.DateTimeField()
    drop_deadline = models.DateTimeField()
    attendance_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    status = models.CharField(max_length=16, choices=CourseSectionStatus.choices, default=CourseSectionStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "section_code", "semester", "academic_year"],
                name="academics_unique_section_per_term",
            )
        ]
        ordering = ["course__course_code", "section_code"]


class SectionTimetable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey("academics.CourseSection", on_delete=models.CASCADE, related_name="timetables")
    day_of_week = models.CharField(max_length=16)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day_of_week", "start_time", "id"]


class EnrollmentStatus(models.TextChoices):
    ENROLLED = "ENROLLED", "Enrolled"
    DROPPED = "DROPPED", "Dropped"
    WAITLISTED = "WAITLISTED", "Waitlisted"
    TRANSFERRED = "TRANSFERRED", "Transferred"


class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="enrollments")
    section = models.ForeignKey("academics.CourseSection", on_delete=models.CASCADE, related_name="enrollments")
    enrollment_status = models.CharField(max_length=16, choices=EnrollmentStatus.choices)
    actor_role = models.CharField(max_length=32)
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollment_actions",
    )
    is_active = models.BooleanField(default=True)
    reason = models.TextField(blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-enrolled_at", "-updated_at"]


class EnrollmentEventType(models.TextChoices):
    ENROLL = "ENROLL", "Enroll"
    DROP = "DROP", "Drop"
    TRANSFER = "TRANSFER", "Transfer"
    WAITLIST = "WAITLIST", "Waitlist"


class EnrollmentEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey("academics.Enrollment", on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=16, choices=EnrollmentEventType.choices)
    actor_role = models.CharField(max_length=32)
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollment_event_actions",
    )
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class WaitlistEntryStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROMOTED = "PROMOTED", "Promoted"
    CANCELLED = "CANCELLED", "Cancelled"


class WaitlistEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="waitlist_entries")
    section = models.ForeignKey("academics.CourseSection", on_delete=models.CASCADE, related_name="waitlist_entries")
    status = models.CharField(max_length=16, choices=WaitlistEntryStatus.choices, default=WaitlistEntryStatus.PENDING)
    promoted_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="promoted_waitlist_entries",
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    promoted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["joined_at", "id"]


class AttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    ABSENT = "ABSENT", "Absent"
    EXCUSED = "EXCUSED", "Excused"


class AttendanceSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey("academics.CourseSection", on_delete=models.CASCADE, related_name="attendance_sessions")
    session_date = models.DateField()
    recorded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_attendance_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class AttendanceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attendance_session = models.ForeignKey("academics.AttendanceSession", on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=16, choices=AttendanceStatus.choices)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attendance_session", "student"],
                name="academics_unique_attendance_record",
            )
        ]


class GradingScaleBand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    letter_grade = models.CharField(max_length=8)
    minimum_score = models.DecimalField(max_digits=5, decimal_places=2)
    maximum_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_points = models.DecimalField(max_digits=4, decimal_places=2)
    is_passing = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-minimum_score"]


class AcademicStandingRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standing = models.CharField(max_length=32, choices=AcademicStanding.choices)
    minimum_gpa = models.DecimalField(max_digits=4, decimal_places=2)
    maximum_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-minimum_gpa"]


class GradeStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    OFFICIAL = "OFFICIAL", "Official"


class SpecialGradeCode(models.TextChoices):
    INCOMPLETE = "I", "Incomplete"
    WITHDRAWN = "W", "Withdrawn"


class GradeRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="grade_records")
    section = models.ForeignKey("academics.CourseSection", on_delete=models.CASCADE, related_name="grade_records")
    numeric_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    letter_grade = models.CharField(max_length=8, blank=True)
    grade_points = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    grade_status = models.CharField(max_length=16, choices=GradeStatus.choices, default=GradeStatus.DRAFT)
    special_code = models.CharField(max_length=8, choices=SpecialGradeCode.choices, blank=True)
    entered_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="entered_grade_records",
    )
    officialised_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="officialised_grade_records",
    )
    entered_at = models.DateTimeField(auto_now_add=True)
    officialised_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "section"],
                name="academics_unique_grade_per_student_section",
            )
        ]


class GradeChangeLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grade_record = models.ForeignKey("academics.GradeRecord", on_delete=models.CASCADE, related_name="change_logs")
    previous_numeric_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_numeric_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    previous_letter_grade = models.CharField(max_length=8, blank=True)
    new_letter_grade = models.CharField(max_length=8, blank=True)
    previous_grade_status = models.CharField(max_length=16, choices=GradeStatus.choices)
    new_grade_status = models.CharField(max_length=16, choices=GradeStatus.choices)
    reason = models.TextField()
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="grade_change_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
