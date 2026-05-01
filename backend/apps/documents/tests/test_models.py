from __future__ import annotations

import pytest

from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument
from apps.documents.tests.factories import make_student, make_user, pdf_upload


@pytest.mark.django_db
def test_student_document_defaults_and_safe_metadata(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user("ADMIN", "doc-model-admin")
    student = make_student("doc-model-student")

    document = StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.TRANSCRIPT,
        title=" Semester 1 Transcript ",
        file=pdf_upload("../../transcript.pdf"),
        original_filename="../../transcript.pdf",
        content_type="application/pdf",
        file_size=24,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
        metadata={"token": "secret-value", "safe": "value"},
    )

    assert document.status == DocumentStatus.PENDING_REVIEW
    assert document.title == "Semester 1 Transcript"
    assert document.original_filename == "transcript.pdf"
    assert document.metadata["token"] == "[REDACTED]"
    assert document.metadata["safe"] == "value"
    assert ".." not in document.file.name
    assert str(student.id) in document.file.name
