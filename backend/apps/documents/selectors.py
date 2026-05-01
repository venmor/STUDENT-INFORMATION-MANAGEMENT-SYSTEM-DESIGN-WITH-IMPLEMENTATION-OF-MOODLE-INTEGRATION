from __future__ import annotations

from datetime import datetime, time

from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from apps.accounts.constants import RoleCode
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument


def visible_documents_for_user(user) -> QuerySet[StudentDocument]:
    queryset = StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by")
    role = getattr(user, "primary_role", None)
    if role == RoleCode.ADMIN:
        return queryset
    if role == RoleCode.STUDENT:
        return queryset.filter(student__user=user, visibility=DocumentVisibility.STUDENT_VISIBLE)
    if role == RoleCode.ADVISOR:
        return queryset.filter(
            student__advisor_assignments__advisor_user=user,
            student__advisor_assignments__is_current=True,
            visibility__in=[DocumentVisibility.ADMIN_ADVISOR, DocumentVisibility.STUDENT_VISIBLE],
        ).distinct()
    return queryset.none()


def parse_datetime_bound(raw_value: str | None, *, end_of_day: bool = False):
    if not raw_value:
        return None
    parsed_date = parse_date(raw_value)
    if parsed_date is not None:
        bound_time = time.max if end_of_day else time.min
        return timezone.make_aware(datetime.combine(parsed_date, bound_time))
    parsed_datetime = parse_datetime(raw_value)
    if parsed_datetime is not None:
        return timezone.make_aware(parsed_datetime) if timezone.is_naive(parsed_datetime) else parsed_datetime
    return None


def apply_document_filters(queryset: QuerySet[StudentDocument], params) -> QuerySet[StudentDocument]:
    student_id = (params.get("student") or "").strip()
    document_type = (params.get("document_type") or params.get("documentType") or "").strip().upper()
    visibility = (params.get("visibility") or "").strip().upper()
    status = (params.get("status") or "").strip().upper()
    uploaded_by = (params.get("uploaded_by") or params.get("uploadedBy") or "").strip()
    search = (params.get("search") or "").strip()
    date_from = parse_datetime_bound(params.get("date_from") or params.get("dateFrom"))
    date_to = parse_datetime_bound(params.get("date_to") or params.get("dateTo"), end_of_day=True)

    if student_id:
        queryset = queryset.filter(student_id=student_id)
    if document_type and document_type != "ALL" and document_type in DocumentType.values:
        queryset = queryset.filter(document_type=document_type)
    if visibility and visibility != "ALL" and visibility in DocumentVisibility.values:
        queryset = queryset.filter(visibility=visibility)
    if status and status != "ALL" and status in DocumentStatus.values:
        queryset = queryset.filter(status=status)
    if uploaded_by:
        queryset = queryset.filter(uploaded_by_id=uploaded_by)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(original_filename__icontains=search)
            | Q(document_type__icontains=search)
            | Q(student__student_number__icontains=search)
            | Q(student__programme__icontains=search)
            | Q(student__user__full_name__icontains=search)
            | Q(student__user__username__icontains=search)
        )
    if date_from is not None:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to is not None:
        queryset = queryset.filter(created_at__lte=date_to)
    return queryset.order_by("-created_at", "-updated_at", "title")
