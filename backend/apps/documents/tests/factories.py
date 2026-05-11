from __future__ import annotations

from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.constants import RoleCode
from apps.students.models import AdvisorAssignment, StudentProfile
from apps.testutils import create_user


def make_user(role: str, username: str):
    return create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=role,
        full_name=username.replace("-", " ").title(),
    )


def make_student(username: str, *, student_number: str | None = None, programme: str = "BSc Computer Science") -> StudentProfile:
    user = make_user(RoleCode.STUDENT, username)
    return StudentProfile.objects.create(
        user=user,
        student_number=student_number or f"2026-CS-{username[-1]}",
        national_id=f"NRC-{username}",
        date_of_birth=date(2004, 1, 15),
        gender="Female",
        programme=programme,
        year_of_study=2,
    )


def assign_advisor(student: StudentProfile, advisor) -> AdvisorAssignment:
    return AdvisorAssignment.objects.create(
        student=student,
        advisor_user=advisor,
        effective_from=date(2026, 4, 15),
        is_current=True,
    )


def pdf_upload(name: str = "transcript.pdf", content: bytes = b"%PDF-1.4\nsafe demo\n%%EOF") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content, content_type="application/pdf")


def png_upload(name: str = "image.png", content: bytes = b"\x89PNG\r\n\x1a\nsafe") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content, content_type="image/png")
