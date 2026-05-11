from __future__ import annotations

from datetime import date

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.constants import RoleCode, STAFF_ROLE_CODES
from apps.accounts.models import User
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument
from apps.documents.validators import calculate_sha256
from apps.students.models import AdvisorAssignment, StudentProfile


DEMO_PASSWORD = "DemoPass123!"
PDF_BYTES = b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n"


class Command(BaseCommand):
    help = "Seed repeatable safe demo student document records and placeholder files."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._upsert_user("admin.demo", "admin.demo@example.edu", "Admin Demo", RoleCode.ADMIN)
        advisor = self._upsert_user("advisor.demo", "advisor.demo@example.edu", "Advisor Demo", RoleCode.ADVISOR)
        student_one = self._upsert_student("student.demo1", "student.demo1@example.edu", "Temba Mwansa", "2026/CS/001", "111111/11/1")
        student_two = self._upsert_student("student.demo2", "student.demo2@example.edu", "Mwila Chanda", "2026/CS/002", "222222/22/2")
        self._assign_advisor(student_one, advisor)
        self._assign_advisor(student_two, advisor)

        created_or_updated = [
            self._upsert_document(
                student=student_one,
                uploaded_by=admin,
                document_type=DocumentType.NRC_ID,
                title="Demo NRC ID",
                description="Safe placeholder NRC/ID document for local workflow testing.",
                original_filename="demo-nrc-id.pdf",
                visibility=DocumentVisibility.ADMIN_ONLY,
                status=DocumentStatus.PENDING_REVIEW,
            ),
            self._upsert_document(
                student=student_one,
                uploaded_by=admin,
                document_type=DocumentType.ADMISSION_LETTER,
                title="Demo Admission Letter",
                description="Safe placeholder admission letter shared with the student.",
                original_filename="demo-admission-letter.pdf",
                visibility=DocumentVisibility.STUDENT_VISIBLE,
                status=DocumentStatus.APPROVED,
                reviewed_by=admin,
            ),
            self._upsert_document(
                student=student_one,
                uploaded_by=admin,
                document_type=DocumentType.TRANSCRIPT,
                title="Demo Transcript",
                description="Safe placeholder transcript available to admin, advisor, and student.",
                original_filename="demo-transcript.pdf",
                visibility=DocumentVisibility.STUDENT_VISIBLE,
                status=DocumentStatus.REJECTED,
                reviewed_by=admin,
                review_note="Demo rejection note for workflow testing.",
            ),
            self._upsert_document(
                student=student_two,
                uploaded_by=student_two.user,
                document_type=DocumentType.APPEAL_LETTER,
                title="Demo Appeal Letter",
                description="Safe placeholder student-uploaded appeal letter awaiting review.",
                original_filename="demo-appeal-letter.pdf",
                visibility=DocumentVisibility.STUDENT_VISIBLE,
                status=DocumentStatus.PENDING_REVIEW,
            ),
            self._upsert_document(
                student=student_two,
                uploaded_by=admin,
                document_type=DocumentType.CLEARANCE_FORM,
                title="Demo Clearance Form",
                description="Safe placeholder archived clearance form.",
                original_filename="demo-clearance-form.pdf",
                visibility=DocumentVisibility.ADMIN_ADVISOR,
                status=DocumentStatus.ARCHIVED,
                reviewed_by=admin,
                review_note="Archived for local demo workflow coverage.",
            ),
            self._upsert_document(
                student=student_two,
                uploaded_by=student_two.user,
                document_type=DocumentType.MEDICAL_SUPPORT,
                title="Demo Medical Support",
                description="Safe placeholder medical/wellbeing supporting document type only.",
                original_filename="demo-medical-support.pdf",
                visibility=DocumentVisibility.STUDENT_VISIBLE,
                status=DocumentStatus.PENDING_REVIEW,
            ),
        ]

        self.stdout.write(self.style.SUCCESS("Demo student documents are ready."))
        self.stdout.write(f"Documents available: {len(created_or_updated)}")
        self.stdout.write("Open /admin/documents as admin.demo or /documents as student.demo1.")

    def _upsert_user(self, username: str, email: str, full_name: str, primary_role: str) -> User:
        user, _ = User.objects.get_or_create(username=username)
        user.email = email
        user.full_name = full_name
        user.primary_role = primary_role
        user.is_active = True
        user.is_staff = primary_role in STAFF_ROLE_CODES
        user.must_reset_password = False
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user

    def _upsert_student(self, username: str, email: str, full_name: str, student_number: str, national_id: str) -> StudentProfile:
        user = self._upsert_user(username, email, full_name, RoleCode.STUDENT)
        student, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "student_number": student_number,
                "national_id": national_id,
                "date_of_birth": date(2003, 1, 15),
                "gender": "Female",
                "programme": "BSc Computer Science",
                "year_of_study": 4,
            },
        )
        student.student_number = student_number
        student.national_id = national_id
        student.date_of_birth = date(2003, 1, 15)
        student.gender = "Female"
        student.programme = "BSc Computer Science"
        student.year_of_study = 4
        student.is_active = True
        student.save()
        return student

    def _assign_advisor(self, student: StudentProfile, advisor: User) -> None:
        AdvisorAssignment.objects.filter(student=student).exclude(advisor_user=advisor).update(is_current=False, effective_to=timezone.localdate())
        AdvisorAssignment.objects.update_or_create(
            student=student,
            advisor_user=advisor,
            defaults={"effective_from": timezone.localdate(), "effective_to": None, "is_current": True},
        )

    def _upsert_document(
        self,
        *,
        student: StudentProfile,
        uploaded_by: User,
        document_type: str,
        title: str,
        description: str,
        original_filename: str,
        visibility: str,
        status: str,
        reviewed_by: User | None = None,
        review_note: str = "",
    ) -> StudentDocument:
        document, _ = StudentDocument.objects.update_or_create(
            student=student,
            document_type=document_type,
            title=title,
            defaults={
                "uploaded_by": uploaded_by,
                "description": description,
                "original_filename": original_filename,
                "content_type": "application/pdf",
                "file_size": len(PDF_BYTES),
                "checksum_sha256": "",
                "visibility": visibility,
                "status": status,
                "reviewed_by": reviewed_by,
                "reviewed_at": timezone.now() if reviewed_by else None,
                "review_note": review_note,
                "metadata": {"demo": True, "source": "seed_document_demo"},
            },
        )
        document.file.save(original_filename, ContentFile(PDF_BYTES), save=False)
        document.file_size = len(PDF_BYTES)
        document.content_type = "application/pdf"
        document.original_filename = original_filename
        document.checksum_sha256 = calculate_sha256(ContentFile(PDF_BYTES))
        document.save()
        return document
