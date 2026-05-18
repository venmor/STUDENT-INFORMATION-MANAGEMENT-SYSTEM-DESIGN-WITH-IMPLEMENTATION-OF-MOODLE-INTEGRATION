from __future__ import annotations

import pytest
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditCategory, AuditEvent
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility
from apps.documents.services import (
    approve_document,
    archive_document,
    get_document_summary,
    reject_document,
    upload_document,
)
from apps.documents.tests.factories import make_student, make_user, pdf_upload
from apps.notifications.models import Notification


@pytest.mark.django_db
def test_upload_review_archive_create_audit_events_and_notifications(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user(RoleCode.ADMIN, "doc-service-admin")
    student = make_student("doc-service-student")

    document = upload_document(
        actor=admin,
        student=student,
        uploaded_file=pdf_upload("official-letter.pdf"),
        document_type=DocumentType.OFFICIAL_LETTER,
        title="Official Letter",
        description="Official student letter.",
        visibility=DocumentVisibility.STUDENT_VISIBLE,
        metadata={"safe": "value", "password": "secret"},
    )

    assert document.status == DocumentStatus.PENDING_REVIEW
    assert document.original_filename == "official-letter.pdf"
    assert document.checksum_sha256
    assert Notification.objects.filter(recipient=student.user, title="Document added").exists()
    upload_audit = AuditEvent.objects.get(action="STUDENT_DOCUMENT_UPLOADED")
    assert upload_audit.category == AuditCategory.DOCUMENT
    assert upload_audit.metadata["documentId"] == str(document.id)
    assert upload_audit.metadata["originalFilename"] == "official-letter.pdf"
    assert "path" not in upload_audit.metadata

    approved = approve_document(document=document, actor=admin, review_note="Verified.", request=None)
    assert approved.status == DocumentStatus.APPROVED
    assert approved.reviewed_by == admin
    assert approved.reviewed_at <= timezone.now()
    assert Notification.objects.filter(recipient=student.user, title="Document approved").exists()

    rejected = reject_document(document=approved, actor=admin, review_note="Replacement required.", request=None)
    assert rejected.status == DocumentStatus.REJECTED
    assert rejected.review_note == "Replacement required."
    assert Notification.objects.filter(recipient=student.user, title="Document rejected").exists()

    archived = archive_document(document=rejected, actor=admin, request=None)
    assert archived.status == DocumentStatus.ARCHIVED

    summary = get_document_summary(admin)
    assert summary["total"] == 1
    assert summary["archived"] == 1
    assert summary["studentVisible"] == 1
    assert summary["byType"][DocumentType.OFFICIAL_LETTER] == 1


@pytest.mark.django_db
def test_student_upload_notifies_admins_and_non_admin_cannot_review(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = make_user(RoleCode.ADMIN, "doc-review-admin")
    student = make_student("doc-review-student")

    document = upload_document(
        actor=student.user,
        student=student,
        uploaded_file=pdf_upload("appeal.pdf"),
        document_type=DocumentType.APPEAL_LETTER,
        title="Appeal Letter",
        description="Student appeal.",
        visibility=DocumentVisibility.ADMIN_ONLY,
        metadata={},
    )

    assert document.visibility == DocumentVisibility.STUDENT_VISIBLE
    assert Notification.objects.filter(recipient=admin, title="Student document awaiting review").exists()
    with pytest.raises(PermissionDenied):
        approve_document(document=document, actor=student.user, review_note="No", request=None)
