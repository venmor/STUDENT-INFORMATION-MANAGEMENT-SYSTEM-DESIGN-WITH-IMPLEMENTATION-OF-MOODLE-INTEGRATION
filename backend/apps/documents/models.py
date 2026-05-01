from __future__ import annotations

import os
import uuid

from django.conf import settings
from django.db import models

from apps.audit.services import sanitize_audit_metadata


class DocumentType(models.TextChoices):
    NRC_ID = "NRC_ID", "NRC/ID"
    ADMISSION_LETTER = "ADMISSION_LETTER", "Admission Letter"
    TRANSCRIPT = "TRANSCRIPT", "Transcript"
    APPEAL_LETTER = "APPEAL_LETTER", "Appeal Letter"
    CLEARANCE_FORM = "CLEARANCE_FORM", "Clearance Form"
    MEDICAL_SUPPORT = "MEDICAL_SUPPORT", "Medical/Wellbeing Supporting Document"
    OTHER = "OTHER", "Other Supporting Document"


class DocumentVisibility(models.TextChoices):
    ADMIN_ONLY = "ADMIN_ONLY", "Admin Only"
    ADMIN_ADVISOR = "ADMIN_ADVISOR", "Admin and Advisor"
    STUDENT_VISIBLE = "STUDENT_VISIBLE", "Student Visible"


class DocumentStatus(models.TextChoices):
    PENDING_REVIEW = "PENDING_REVIEW", "Pending Review"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    ARCHIVED = "ARCHIVED", "Archived"


def student_document_upload_path(instance: "StudentDocument", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    return f"student_documents/{instance.student_id}/{instance.id}{extension}"


class StudentDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_student_documents",
    )
    document_type = models.CharField(max_length=32, choices=DocumentType.choices)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=student_document_upload_path)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=160)
    file_size = models.PositiveIntegerField()
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    visibility = models.CharField(
        max_length=24,
        choices=DocumentVisibility.choices,
        default=DocumentVisibility.ADMIN_ONLY,
    )
    status = models.CharField(
        max_length=24,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING_REVIEW,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_student_documents",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-updated_at", "title"]
        indexes = [
            models.Index(fields=["student", "status", "-created_at"], name="doc_student_status_idx"),
            models.Index(fields=["document_type", "status"], name="doc_type_status_idx"),
            models.Index(fields=["visibility", "status"], name="doc_visibility_status_idx"),
            models.Index(fields=["uploaded_by", "-created_at"], name="doc_uploaded_by_idx"),
        ]

    def save(self, *args, **kwargs):
        from .validators import sanitize_original_filename

        self.title = self.title.strip()
        self.original_filename = sanitize_original_filename(self.original_filename)
        self.metadata = sanitize_audit_metadata(self.metadata)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student.student_number}:{self.document_type}:{self.title}"
