from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.accounts.constants import RoleCode
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument
from apps.documents.services import get_document_report
from apps.documents.tests.factories import make_student, make_user, pdf_upload
from apps.testutils import authenticated_client_for_user


@pytest.mark.django_db
def test_document_reporting_counts(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user(RoleCode.ADMIN, "doc-report-admin")
    student = make_student("doc-report-student")
    StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.TRANSCRIPT,
        title="Pending Transcript",
        file=pdf_upload("pending.pdf"),
        original_filename="pending.pdf",
        content_type="application/pdf",
        file_size=24,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
    )
    StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.NRC_ID,
        title="Rejected NRC",
        file=pdf_upload("rejected.pdf"),
        original_filename="rejected.pdf",
        content_type="application/pdf",
        file_size=24,
        visibility=DocumentVisibility.ADMIN_ONLY,
        status=DocumentStatus.REJECTED,
    )
    client = authenticated_client_for_user(admin)

    report = get_document_report()
    response = client.get("/api/v1/admin/reports/documents/")

    assert report["summary"]["total"] == 2
    assert report["summary"]["pendingReview"] == 1
    assert report["summary"]["rejected"] == 1
    assert response.status_code == 200
    assert response.json()["summary"]["pendingReview"] == 1


@pytest.mark.django_db
def test_seed_document_demo_creates_idempotent_downloadable_files(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    call_command("seed_document_demo")
    first_count = StudentDocument.objects.count()
    first_files = {document.original_filename for document in StudentDocument.objects.all()}
    call_command("seed_document_demo")

    assert first_count >= 4
    assert StudentDocument.objects.count() == first_count
    assert {"demo-nrc-id.pdf", "demo-admission-letter.pdf", "demo-transcript.pdf"}.issubset(first_files)
    assert all(document.file.storage.exists(document.file.name) for document in StudentDocument.objects.all())
