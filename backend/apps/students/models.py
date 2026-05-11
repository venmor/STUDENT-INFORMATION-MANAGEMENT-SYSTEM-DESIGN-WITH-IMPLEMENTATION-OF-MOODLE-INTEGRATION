from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AcademicStanding(models.TextChoices):
    GOOD_STANDING = "GOOD_STANDING", "Good Standing"
    ACADEMIC_WARNING = "ACADEMIC_WARNING", "Academic Warning"
    PROBATION = "PROBATION", "Probation"
    SUSPENDED = "SUSPENDED", "Suspended"


class AdvisingNoteStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    APPROVED = "APPROVED", "Approved"


class StudentCorrectionRequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_profile",
    )
    student_number = models.CharField(max_length=32, unique=True)
    national_id = models.CharField(max_length=64, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=32)
    programme = models.CharField(max_length=128)
    programme_ref = models.ForeignKey(
        "structure.Programme", on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    year_of_study = models.PositiveSmallIntegerField()
    academic_standing = models.CharField(
        max_length=32,
        choices=AcademicStanding.choices,
        default=AcademicStanding.GOOD_STANDING,
    )
    cumulative_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    standing_override_reason = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student_number"]

    def __str__(self) -> str:
        return self.student_number


class AdvisorAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="advisor_assignments",
    )
    advisor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_advisee_records",
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-effective_from", "-created_at"]

    def __str__(self) -> str:
        return f"{self.student.student_number}:{self.advisor_user.username}"


class FinancialFlag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="financial_flags",
    )
    flag_type = models.CharField(max_length=64)
    reason = models.TextField()
    effective_date = models.DateField()
    cleared_date = models.DateField(null=True, blank=True)
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_financial_flags",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-effective_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.student.student_number}:{self.flag_type}"


class AdvisingNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="advising_notes",
    )
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_advising_notes",
    )
    note_text = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=AdvisingNoteStatus.choices,
        default=AdvisingNoteStatus.DRAFT,
    )
    approved_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_advising_notes",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.student.student_number}:{self.status}"


class StudentCorrectionRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="correction_requests",
    )
    requested_changes = models.JSONField(default=dict)
    justification = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=StudentCorrectionRequestStatus.choices,
        default=StudentCorrectionRequestStatus.PENDING,
    )
    review_note = models.TextField(blank=True)
    reviewed_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reviewed_student_correction_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-updated_at"]

    def __str__(self) -> str:
        return f"{self.student.student_number}:{self.status}"
