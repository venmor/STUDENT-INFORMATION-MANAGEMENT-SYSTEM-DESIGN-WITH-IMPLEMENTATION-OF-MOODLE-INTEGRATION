from __future__ import annotations

from datetime import datetime, time, timedelta

from django.db.models import Count, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditCategory, AuditEvent, AuditSeverity

from .serializers import AuditEventSerializer


LIST_LIMIT_DEFAULT = 100
LIST_LIMIT_MAX = 250


def bounded_limit(raw_limit: str | None, *, default: int = LIST_LIMIT_DEFAULT, maximum: int = LIST_LIMIT_MAX) -> int:
    try:
        requested = int(raw_limit or default)
    except (TypeError, ValueError):
        return default
    return max(1, min(requested, maximum))


def parse_datetime_bound(raw_value: str | None, *, end_of_day: bool = False):
    if not raw_value:
        return None
    parsed_datetime = parse_datetime(raw_value)
    if parsed_datetime is not None:
        if timezone.is_naive(parsed_datetime):
            return timezone.make_aware(parsed_datetime)
        return parsed_datetime
    parsed_date = parse_date(raw_value)
    if parsed_date is None:
        return None
    bound_time = time.max if end_of_day else time.min
    return timezone.make_aware(datetime.combine(parsed_date, bound_time))


def filter_activity_queryset(request) -> QuerySet[AuditEvent]:
    queryset = AuditEvent.objects.select_related("actor").order_by("-created_at", "-id")
    category = (request.query_params.get("category") or "").strip().upper()
    severity = (request.query_params.get("severity") or "").strip().upper()
    action = (request.query_params.get("action") or "").strip().upper()
    actor = (request.query_params.get("actor") or "").strip()
    search = (request.query_params.get("search") or "").strip()
    date_from = parse_datetime_bound(request.query_params.get("date_from"))
    date_to = parse_datetime_bound(request.query_params.get("date_to"), end_of_day=True)

    if category and category != "ALL" and category in AuditCategory.values:
        queryset = queryset.filter(category=category)
    if severity and severity != "ALL" and severity in AuditSeverity.values:
        queryset = queryset.filter(severity=severity)
    if action:
        queryset = queryset.filter(action__icontains=action)
    if actor:
        queryset = queryset.filter(
            Q(actor_username__icontains=actor)
            | Q(actor_role__icontains=actor)
            | Q(actor__username__icontains=actor)
            | Q(actor__full_name__icontains=actor)
        )
    if search:
        queryset = queryset.filter(
            Q(summary__icontains=search)
            | Q(action__icontains=search)
            | Q(actor_username__icontains=search)
            | Q(actor_role__icontains=search)
            | Q(actor__username__icontains=search)
            | Q(actor__full_name__icontains=search)
            | Q(target_type__icontains=search)
            | Q(target_id__icontains=search)
        )
    if date_from is not None:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to is not None:
        queryset = queryset.filter(created_at__lte=date_to)
    return queryset


class AuditActivityListView(APIView):
    def get(self, request):
        queryset = filter_activity_queryset(request)
        limit = bounded_limit(request.query_params.get("limit"))
        serializer = AuditEventSerializer(queryset[:limit], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuditActivitySummaryView(APIView):
    def get(self, request):
        queryset = AuditEvent.objects.all()
        counts = {
            item["category"]: item["count"]
            for item in queryset.values("category").annotate(count=Count("id"))
        }
        today_start = timezone.make_aware(datetime.combine(timezone.localdate(), time.min))
        today_end = today_start + timedelta(days=1)
        return Response(
            {
                "total": queryset.count(),
                "errors": queryset.filter(severity=AuditSeverity.ERROR).count(),
                "warnings": queryset.filter(severity=AuditSeverity.WARNING).count(),
                "today": queryset.filter(created_at__gte=today_start, created_at__lt=today_end).count(),
                "byCategory": {category: counts.get(category, 0) for category in AuditCategory.values},
            },
            status=status.HTTP_200_OK,
        )


class AuditActivityDetailView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(AuditEvent.objects.select_related("actor"), pk=event_id)
        return Response(AuditEventSerializer(event).data, status=status.HTTP_200_OK)
