from __future__ import annotations

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditEvent
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument
from apps.documents.tests.factories import assign_advisor, make_student, make_user, pdf_upload, png_upload
from apps.testutils import authenticated_client_for_user


@pytest.mark.django_db
def test_document_api_enforces_role_visibility_and_download(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user(RoleCode.ADMIN, "doc-api-admin")
    advisor = make_user(RoleCode.ADVISOR, "doc-api-advisor")
    faculty = make_user(RoleCode.FACULTY, "doc-api-faculty")
    student = make_student("doc-api-student", student_number="2026-DOC-A")
    other_student = make_student("doc-api-other", student_number="2026-DOC-B")
    assign_advisor(student, advisor)
    admin_only = StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.NRC_ID,
        title="NRC",
        file=pdf_upload("nrc.pdf"),
        original_filename="nrc.pdf",
        content_type="application/pdf",
        file_size=24,
        visibility=DocumentVisibility.ADMIN_ONLY,
    )
    student_visible = StudentDocument.objects.create(
        student=student,
        uploaded_by=admin,
        document_type=DocumentType.TRANSCRIPT,
        title="Transcript",
        file=pdf_upload("transcript.pdf"),
        original_filename="transcript.pdf",
        content_type="application/pdf",
        file_size=24,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
    )
    StudentDocument.objects.create(
        student=other_student,
        uploaded_by=admin,
        document_type=DocumentType.OTHER,
        title="Other Student",
        file=pdf_upload("other.pdf"),
        original_filename="other.pdf",
        content_type="application/pdf",
        file_size=24,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
    )

    admin_client = authenticated_client_for_user(admin)
    student_client = authenticated_client_for_user(student.user)
    advisor_client = authenticated_client_for_user(advisor)
    faculty_client = authenticated_client_for_user(faculty)

    assert len(admin_client.get("/api/v1/documents").json()) == 3
    student_response = student_client.get("/api/v1/documents")
    assert student_response.status_code == 200
    assert [item["id"] for item in student_response.json()] == [str(student_visible.id)]
    advisor_response = advisor_client.get("/api/v1/documents")
    assert advisor_response.status_code == 200
    assert [item["id"] for item in advisor_response.json()] == [str(student_visible.id)]
    assert faculty_client.get("/api/v1/documents").status_code == 403

    denied_detail = student_client.get(f"/api/v1/documents/{admin_only.id}")
    assert denied_detail.status_code == 403

    download_response = student_client.get(f"/api/v1/documents/{student_visible.id}/download")
    assert download_response.status_code == 200
    assert "transcript.pdf" in download_response["Content-Disposition"]
    assert "student_documents" not in download_response["Content-Disposition"]
    assert AuditEvent.objects.filter(action="STUDENT_DOCUMENT_DOWNLOADED", target_id=str(student_visible.id)).exists()

    denied_download = student_client.get(f"/api/v1/documents/{admin_only.id}/download")
    assert denied_download.status_code == 403


@pytest.mark.django_db
def test_admin_upload_validation_review_archive_and_summary(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.STUDENT_DOCUMENT_MAX_UPLOAD_SIZE = 32
    admin = make_user(RoleCode.ADMIN, "doc-api-upload-admin")
    student = make_student("doc-api-upload-student")
    admin_client = authenticated_client_for_user(admin)
    student_client = authenticated_client_for_user(student.user)

    response = admin_client.post(
        "/api/v1/documents",
        {
            "student": str(student.id),
            "documentType": DocumentType.TRANSCRIPT,
            "title": "Semester Transcript",
            "description": "Uploaded transcript.",
            "visibility": DocumentVisibility.STUDENT_VISIBLE,
            "metadata": '{"safe":"value","token":"secret"}',
            "file": pdf_upload("semester-transcript.pdf"),
        },
        format="multipart",
    )
    assert response.status_code == 201, response.json()
    document_id = response.json()["id"]
    assert response.json()["canDownload"] is True
    assert response.json()["metadata"]["token"] == "[REDACTED]"
    assert "file" not in response.json()
    assert "path" not in str(response.json()).lower()

    invalid = admin_client.post(
        "/api/v1/documents",
        {
            "student": str(student.id),
            "documentType": DocumentType.OTHER,
            "title": "Invalid",
            "visibility": DocumentVisibility.ADMIN_ONLY,
            "file": SimpleUploadedFile("invalid.txt", b"text", content_type="text/plain"),
        },
        format="multipart",
    )
    assert invalid.status_code == 400
    assert "Unsupported" in str(invalid.json())

    empty = admin_client.post(
        "/api/v1/documents",
        {
            "student": str(student.id),
            "documentType": DocumentType.OTHER,
            "title": "Empty",
            "visibility": DocumentVisibility.ADMIN_ONLY,
            "file": SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf"),
        },
        format="multipart",
    )
    assert empty.status_code == 400

    oversized = admin_client.post(
        "/api/v1/documents",
        {
            "student": str(student.id),
            "documentType": DocumentType.OTHER,
            "title": "Oversized",
            "visibility": DocumentVisibility.ADMIN_ONLY,
            "file": SimpleUploadedFile("oversized.pdf", b"1" * 33, content_type="application/pdf"),
        },
        format="multipart",
    )
    assert oversized.status_code == 400

    assert student_client.post(f"/api/v1/documents/{document_id}/approve", {"reviewNote": "No"}, format="json").status_code == 403
    approve = admin_client.post(f"/api/v1/documents/{document_id}/approve", {"reviewNote": "Verified."}, format="json")
    assert approve.status_code == 200, approve.json()
    assert approve.json()["status"] == DocumentStatus.APPROVED

    reject = admin_client.post(f"/api/v1/documents/{document_id}/reject", {"reviewNote": "Replacement needed."}, format="json")
    assert reject.status_code == 200, reject.json()
    assert reject.json()["status"] == DocumentStatus.REJECTED
    assert reject.json()["reviewNote"] == "Replacement needed."

    archive = admin_client.post(f"/api/v1/documents/{document_id}/archive", format="json")
    assert archive.status_code == 200, archive.json()
    assert archive.json()["status"] == DocumentStatus.ARCHIVED

    summary = admin_client.get("/api/v1/documents/summary").json()
    assert summary["total"] == 1
    assert summary["archived"] == 1
    assert summary["studentVisible"] == 1


@pytest.mark.django_db
def test_student_self_endpoint_uploads_supporting_documents(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user(RoleCode.ADMIN, "doc-api-self-admin")
    student = make_student("doc-api-self-student")
    client = authenticated_client_for_user(student.user)

    response = client.post(
        "/api/v1/me/documents",
        {
            "documentType": DocumentType.MEDICAL_SUPPORT,
            "title": "Medical Support",
            "description": "Supporting document.",
            "visibility": DocumentVisibility.ADMIN_ONLY,
            "file": png_upload("support.png"),
        },
        format="multipart",
    )

    assert response.status_code == 201, response.json()
    assert response.json()["visibility"] == DocumentVisibility.STUDENT_VISIBLE
    assert response.json()["status"] == DocumentStatus.PENDING_REVIEW
    assert response.json()["uploadedBy"]["id"] == student.user.id
    assert admin.notifications.filter(title="Student document awaiting review").exists()
