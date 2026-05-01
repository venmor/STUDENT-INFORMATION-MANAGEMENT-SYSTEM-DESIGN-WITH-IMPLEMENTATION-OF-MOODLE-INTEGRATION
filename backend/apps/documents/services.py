from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.db.models import Count, QuerySet
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely, sanitize_audit_metadata
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument
from apps.documents.permissions import (
    can_archive_document,
    can_download_document,
    can_review_document,
    can_update_document,
    can_upload_document_for_student,
)
from apps.documents.selectors import visible_documents_for_user
from apps.documents.validators import calculate_sha256, sanitize_original_filename, validate_document_upload
from apps.students.models import StudentProfile


logger = logging.getLogger(__name__)


def document_audit_metadata(document: StudentDocument) -> dict[str, Any]:
    return {
        "documentId": str(document.id),
        "studentId": str(document.student_id),
        "documentType": document.document_type,
        "visibility": document.visibility,
        "status": document.status,
        "originalFilename": document.original_filename,
        "fileSize": document.file_size,
        "contentType": document.content_type,
    }


def record_document_audit(
    *,
    actor,
    action: str,
    summary: str,
    document: StudentDocument,
    severity: str = AuditSeverity.INFO,
    metadata: dict[str, Any] | None = None,
    request=None,
) -> None:
    safe_metadata = document_audit_metadata(document)
    safe_metadata.update(sanitize_audit_metadata(metadata or {}))
    record_audit_event_safely(
        actor=actor,
        category=AuditCategory.DOCUMENT,
        action=action,
        summary=summary,
        target_type="StudentDocument",
        target_id=str(document.id),
        severity=severity,
        metadata=safe_metadata,
        request=request,
    )


def notify_document_uploaded(document: StudentDocument, *, actor) -> None:
    try:
        from apps.notifications.models import NotificationCategory, NotificationSeverity
        from apps.notifications.services import create_notification, notify_admins
    except Exception:
        logger.exception("Failed to import notification services for document %s", document.id)
        return

    metadata = {
        "documentId": str(document.id),
        "studentId": str(document.student_id),
        "documentType": document.document_type,
        "status": document.status,
        "visibility": document.visibility,
    }
    if getattr(actor, "primary_role", None) == RoleCode.STUDENT:
        notify_admins(
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.WARNING,
            title="Student document awaiting review",
            message=f"{document.student.user.full_name or document.student.user.username} uploaded {document.title} for review.",
            action_label="Open documents",
            action_url="/admin/documents",
            source_type="StudentDocument",
            source_id=str(document.id),
            metadata=metadata,
        )
        return

    if document.visibility == DocumentVisibility.STUDENT_VISIBLE:
        create_notification(
            recipient=document.student.user,
            category=NotificationCategory.ACADEMIC,
            severity=NotificationSeverity.INFO,
            title="Document added",
            message=f"{document.title} has been added to your student documents.",
            action_label="Open documents",
            action_url="/documents",
            source_type="StudentDocument",
            source_id=str(document.id),
            metadata=metadata,
        )


def notify_document_reviewed(document: StudentDocument, *, title: str, message: str, severity: str) -> None:
    if document.visibility != DocumentVisibility.STUDENT_VISIBLE and document.uploaded_by_id != document.student.user_id:
        return
    try:
        from apps.notifications.models import NotificationCategory
        from apps.notifications.services import create_notification
    except Exception:
        logger.exception("Failed to import notification services for document review %s", document.id)
        return

    create_notification(
        recipient=document.student.user,
        category=NotificationCategory.ACADEMIC,
        severity=severity,
        title=title,
        message=message,
        action_label="Open documents",
        action_url="/documents",
        source_type="StudentDocument",
        source_id=str(document.id),
        metadata={
            "documentId": str(document.id),
            "documentType": document.document_type,
            "status": document.status,
            "visibility": document.visibility,
        },
    )


@transaction.atomic
def upload_document(
    *,
    actor,
    student: StudentProfile,
    uploaded_file,
    document_type: str,
    title: str,
    description: str = "",
    visibility: str = DocumentVisibility.ADMIN_ONLY,
    metadata: dict[str, Any] | None = None,
    request=None,
) -> StudentDocument:
    if not can_upload_document_for_student(actor, student):
        raise PermissionDenied("You do not have permission to upload documents for this student.")
    validate_document_upload(uploaded_file)
    original_filename = sanitize_original_filename(uploaded_file.name)
    effective_visibility = DocumentVisibility.STUDENT_VISIBLE if getattr(actor, "primary_role", None) == RoleCode.STUDENT else visibility
    document = StudentDocument.objects.create(
        student=student,
        uploaded_by=actor if getattr(actor, "pk", None) else None,
        document_type=document_type,
        title=title,
        description=description,
        file=uploaded_file,
        original_filename=original_filename,
        content_type=(uploaded_file.content_type or "").lower(),
        file_size=uploaded_file.size,
        checksum_sha256=calculate_sha256(uploaded_file),
        visibility=effective_visibility,
        metadata=sanitize_audit_metadata(metadata or {}),
    )
    record_document_audit(
        actor=actor,
        action="STUDENT_DOCUMENT_UPLOADED",
        summary=f"Student document {document.title} was uploaded.",
        document=document,
        severity=AuditSeverity.SUCCESS,
        request=request,
    )
    notify_document_uploaded(document, actor=actor)
    return document


@transaction.atomic
def update_document(
    *,
    document: StudentDocument,
    actor,
    fields: dict[str, Any],
    request=None,
) -> StudentDocument:
    if not can_update_document(actor, document):
        raise PermissionDenied("Admin access is required to update documents.")
    allowed_fields = {"document_type", "title", "description", "visibility", "metadata"}
    changed_fields = []
    for field_name, value in fields.items():
        if field_name not in allowed_fields:
            continue
        setattr(document, field_name, sanitize_audit_metadata(value) if field_name == "metadata" else value)
        changed_fields.append(field_name)
    if changed_fields:
        document.save(update_fields=[*changed_fields, "updated_at"])
        record_document_audit(
            actor=actor,
            action="STUDENT_DOCUMENT_UPDATED",
            summary=f"Student document {document.title} was updated.",
            document=document,
            metadata={"changedFields": sorted(changed_fields)},
            request=request,
        )
    return document


@transaction.atomic
def approve_document(*, document: StudentDocument, actor, review_note: str = "", request=None) -> StudentDocument:
    if not can_review_document(actor, document):
        raise PermissionDenied("Admin access is required to review documents.")
    document.status = DocumentStatus.APPROVED
    document.reviewed_by = actor
    document.reviewed_at = timezone.now()
    document.review_note = review_note.strip()
    document.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "updated_at"])
    record_document_audit(
        actor=actor,
        action="STUDENT_DOCUMENT_APPROVED",
        summary=f"Student document {document.title} was approved.",
        document=document,
        severity=AuditSeverity.SUCCESS,
        metadata={"reviewNotePresent": bool(document.review_note)},
        request=request,
    )
    from apps.notifications.models import NotificationSeverity

    notify_document_reviewed(
        document,
        title="Document approved",
        message=f"{document.title} has been approved.",
        severity=NotificationSeverity.SUCCESS,
    )
    return document


@transaction.atomic
def reject_document(*, document: StudentDocument, actor, review_note: str = "", request=None) -> StudentDocument:
    if not can_review_document(actor, document):
        raise PermissionDenied("Admin access is required to review documents.")
    document.status = DocumentStatus.REJECTED
    document.reviewed_by = actor
    document.reviewed_at = timezone.now()
    document.review_note = review_note.strip()
    document.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "updated_at"])
    record_document_audit(
        actor=actor,
        action="STUDENT_DOCUMENT_REJECTED",
        summary=f"Student document {document.title} was rejected.",
        document=document,
        severity=AuditSeverity.WARNING,
        metadata={"reviewNotePresent": bool(document.review_note)},
        request=request,
    )
    from apps.notifications.models import NotificationSeverity

    notify_document_reviewed(
        document,
        title="Document rejected",
        message=f"{document.title} was rejected. Review note: {document.review_note or 'No review note provided.'}",
        severity=NotificationSeverity.WARNING,
    )
    return document


@transaction.atomic
def archive_document(*, document: StudentDocument, actor, request=None) -> StudentDocument:
    if not can_archive_document(actor, document):
        raise PermissionDenied("Admin access is required to archive documents.")
    document.status = DocumentStatus.ARCHIVED
    document.save(update_fields=["status", "updated_at"])
    record_document_audit(
        actor=actor,
        action="STUDENT_DOCUMENT_ARCHIVED",
        summary=f"Student document {document.title} was archived.",
        document=document,
        severity=AuditSeverity.WARNING,
        request=request,
    )
    return document


def require_download_permission(*, document: StudentDocument, actor, request=None) -> StudentDocument:
    if not can_download_document(actor, document):
        raise PermissionDenied("You do not have permission to download this document.")
    record_document_audit(
        actor=actor,
        action="STUDENT_DOCUMENT_DOWNLOADED",
        summary=f"Student document {document.title} was downloaded.",
        document=document,
        request=request,
    )
    return document


def _summary_from_queryset(queryset: QuerySet[StudentDocument]) -> dict[str, Any]:
    now = timezone.now()
    recent_cutoff = now - timedelta(days=7)
    by_type_counts = {
        row["document_type"]: row["count"]
        for row in queryset.values("document_type").annotate(count=Count("id"))
    }
    return {
        "total": queryset.count(),
        "pendingReview": queryset.filter(status=DocumentStatus.PENDING_REVIEW).count(),
        "approved": queryset.filter(status=DocumentStatus.APPROVED).count(),
        "rejected": queryset.filter(status=DocumentStatus.REJECTED).count(),
        "archived": queryset.filter(status=DocumentStatus.ARCHIVED).count(),
        "studentVisible": queryset.filter(visibility=DocumentVisibility.STUDENT_VISIBLE).count(),
        "adminOnly": queryset.filter(visibility=DocumentVisibility.ADMIN_ONLY).count(),
        "recentUploads": queryset.filter(created_at__gte=recent_cutoff).count(),
        "byType": {document_type: by_type_counts.get(document_type, 0) for document_type in DocumentType.values},
    }


def get_document_summary(user) -> dict[str, Any]:
    return _summary_from_queryset(visible_documents_for_user(user))


def get_document_report() -> dict[str, Any]:
    queryset = StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by")
    summary = _summary_from_queryset(queryset)
    recent = queryset.order_by("-created_at")[:8]
    return {
        "summary": summary,
        "recentDocuments": [
            {
                "id": str(document.id),
                "studentNumber": document.student.student_number,
                "studentName": document.student.user.full_name or document.student.user.username,
                "documentType": document.document_type,
                "title": document.title,
                "visibility": document.visibility,
                "status": document.status,
                "createdAt": document.created_at,
            }
            for document in recent
        ],
    }
