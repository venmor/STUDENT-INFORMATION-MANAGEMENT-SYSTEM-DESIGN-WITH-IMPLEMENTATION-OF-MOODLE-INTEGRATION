from __future__ import annotations

import pytest

from apps.accounts.constants import RoleCode
from apps.documents.models import DocumentType, DocumentVisibility, StudentDocument
from apps.documents.permissions import can_archive_document, can_download_document, can_review_document
from apps.documents.selectors import visible_documents_for_user
from apps.documents.tests.factories import assign_advisor, make_student, make_user, pdf_upload


@pytest.mark.django_db
def test_visible_documents_follow_admin_student_advisor_and_faculty_boundaries(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user(RoleCode.ADMIN, "doc-perm-admin")
    advisor = make_user(RoleCode.ADVISOR, "doc-perm-advisor")
    unassigned_advisor = make_user(RoleCode.ADVISOR, "doc-perm-stranger")
    faculty = make_user(RoleCode.FACULTY, "doc-perm-faculty")
    student = make_student("doc-perm-student", student_number="2026-DOC-1")
    other_student = make_student("doc-perm-other", student_number="2026-DOC-2")
    assign_advisor(student, advisor)

    admin_only = StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.NRC_ID,
        title="NRC",
        file=pdf_upload("nrc.pdf"),
        original_filename="nrc.pdf",
        content_type="application/pdf",
        file_size=10,
        visibility=DocumentVisibility.ADMIN_ONLY,
    )
    advisor_visible = StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.TRANSCRIPT,
        title="Transcript",
        file=pdf_upload("transcript.pdf"),
        original_filename="transcript.pdf",
        content_type="application/pdf",
        file_size=10,
        visibility=DocumentVisibility.ADMIN_ADVISOR,
    )
    student_visible = StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.ADMISSION_LETTER,
        title="Admission Letter",
        file=pdf_upload("letter.pdf"),
        original_filename="letter.pdf",
        content_type="application/pdf",
        file_size=10,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
    )
    other_document = StudentDocument.objects.create(
        student=other_student,
        uploaded_by=admin,
        document_type=DocumentType.OTHER,
        title="Other Student",
        file=pdf_upload("other.pdf"),
        original_filename="other.pdf",
        content_type="application/pdf",
        file_size=10,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
    )

    assert set(visible_documents_for_user(admin)) == {admin_only, advisor_visible, student_visible, other_document}
    assert set(visible_documents_for_user(advisor)) == {advisor_visible, student_visible}
    assert list(visible_documents_for_user(unassigned_advisor)) == []
    assert list(visible_documents_for_user(faculty)) == []
    assert set(visible_documents_for_user(student.user)) == {student_visible}

    assert can_download_document(admin, admin_only)
    assert can_download_document(advisor, advisor_visible)
    assert not can_download_document(advisor, admin_only)
    assert can_download_document(student.user, student_visible)
    assert not can_download_document(student.user, advisor_visible)
    assert not can_download_document(faculty, student_visible)
    assert can_review_document(admin, student_visible)
    assert can_archive_document(admin, student_visible)
    assert not can_review_document(advisor, student_visible)
    assert not can_archive_document(student.user, student_visible)
