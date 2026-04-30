from __future__ import annotations

from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.integration.services import process_outbox_event

from .serializers import (
    MoodleCourseMapSerializer,
    MoodleEngagementRunSerializer,
    MoodleEngagementSnapshotSerializer,
    MoodleOutboxEventSerializer,
    MoodleUserMapSerializer,
    summarize_outbox_payload,
)


LIST_LIMIT = 100


def _setting_present(name: str) -> bool:
    return bool(getattr(settings, name, ""))


def _moodle_rest_config_status() -> str:
    return "present" if _setting_present("MOODLE_BASE_URL") and _setting_present("MOODLE_WS_TOKEN") else "missing"


def _lti_config_status() -> str:
    issuer_allowlist = getattr(settings, "LTI_PLATFORM_ISSUER_ALLOWLIST", [])
    private_key_present = _setting_present("LTI_PRIVATE_KEY") or _setting_present("LTI_PRIVATE_KEY_FILE")
    public_key_present = _setting_present("LTI_PUBLIC_KEY") or _setting_present("LTI_PUBLIC_KEY_FILE")
    required_values_present = (
        _setting_present("LTI_CLIENT_ID")
        and _setting_present("LTI_DEPLOYMENT_ID")
        and bool(issuer_allowlist)
        and private_key_present
        and public_key_present
    )
    return "present" if required_values_present else "missing"


def _latest_engagement_payload() -> dict:
    latest_run = MoodleEngagementIngestionRun.objects.order_by("-started_at").first()
    if latest_run is None:
        return {
            "latestRunStatus": None,
            "latestRunStartedAt": None,
            "latestRunCompletedAt": None,
            "latestRunSnapshots": 0,
            "latestRunFailures": 0,
        }
    return {
        "latestRunStatus": latest_run.status,
        "latestRunStartedAt": latest_run.started_at,
        "latestRunCompletedAt": latest_run.completed_at,
        "latestRunSnapshots": latest_run.snapshots_created + latest_run.snapshots_updated,
        "latestRunFailures": latest_run.failure_count,
    }


def _summary_payload() -> dict:
    pending = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.PENDING).count()
    processed = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.PROCESSED).count()
    failed = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.FAILED).count()
    return {
        "outbox": {
            "pending": pending,
            "processed": processed,
            "failed": failed,
            "retryable": pending + failed,
        },
        "mappings": {
            "users": MoodleUserMap.objects.count(),
            "courses": MoodleCourseMap.objects.count(),
        },
        "engagement": _latest_engagement_payload(),
        "readiness": {
            "moodleRestConfig": _moodle_rest_config_status(),
            "ltiConfig": _lti_config_status(),
        },
    }


def _matches_search(event: IntegrationOutboxEvent, search: str) -> bool:
    needle = search.strip().lower()
    if not needle:
        return True
    haystacks = [str(event.id), event.event_type]
    summary = summarize_outbox_payload(event.payload)
    haystacks.extend(str(value) for value in summary.values() if value not in (None, ""))
    return any(needle in value.lower() for value in haystacks)


class MoodleSyncSummaryView(APIView):
    def get(self, request):
        return Response(_summary_payload(), status=status.HTTP_200_OK)


class MoodleOutboxEventListView(APIView):
    def get_queryset(self) -> QuerySet[IntegrationOutboxEvent]:
        queryset = IntegrationOutboxEvent.objects.order_by("-created_at")
        status_filter = self.request.query_params.get("status", "").strip().upper()
        event_type_filter = self.request.query_params.get("event_type", "").strip().upper()
        if status_filter and status_filter != "ALL":
            queryset = queryset.filter(status=status_filter)
        if event_type_filter and event_type_filter != "ALL":
            queryset = queryset.filter(event_type=event_type_filter)
        return queryset

    def get(self, request):
        queryset = list(self.get_queryset()[:LIST_LIMIT])
        search = request.query_params.get("search", "")
        if search:
            queryset = [event for event in queryset if _matches_search(event, search)]
        serializer = MoodleOutboxEventSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MoodleOutboxEventRetryView(APIView):
    def post(self, request, event_id):
        event = get_object_or_404(IntegrationOutboxEvent, pk=event_id)
        if event.status == IntegrationEventStatus.PROCESSED:
            return Response(
                {"detail": "Processed Moodle sync events cannot be retried."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        succeeded = process_outbox_event(event.id)
        event.refresh_from_db()
        try:
            from apps.audit.services import record_audit_event_safely

            record_audit_event_safely(
                actor=request.user,
                category="MOODLE",
                action="MOODLE_SYNC_RETRIED",
                summary=f"Moodle sync retry {'succeeded' if succeeded else 'failed'} for {event.event_type}.",
                target_type="IntegrationOutboxEvent",
                target_id=str(event.id),
                severity="SUCCESS" if succeeded else "ERROR",
                metadata={
                    "eventType": event.event_type,
                    "result": "SUCCEEDED" if succeeded else "FAILED",
                    "attempts": event.attempts,
                    "safeError": event.last_error or "",
                },
                request=request,
            )
        except Exception:
            pass
        serializer = MoodleOutboxEventSerializer(event)
        if not succeeded:
            return Response(
                {
                    "detail": "Moodle sync retry failed safely.",
                    "event": serializer.data,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)


class MoodleUserMapListView(APIView):
    def get(self, request):
        queryset = MoodleUserMap.objects.select_related("user").order_by("-last_synced_at")[:LIST_LIMIT]
        serializer = MoodleUserMapSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MoodleCourseMapListView(APIView):
    def get(self, request):
        queryset = MoodleCourseMap.objects.select_related("section__course").order_by("-last_synced_at")[:LIST_LIMIT]
        serializer = MoodleCourseMapSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MoodleEngagementRunListView(APIView):
    def get(self, request):
        queryset = MoodleEngagementIngestionRun.objects.order_by("-started_at")[:25]
        serializer = MoodleEngagementRunSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MoodleEngagementSnapshotListView(APIView):
    def get(self, request):
        queryset = (
            MoodleEngagementSnapshot.objects.select_related("user", "student", "section__course")
            .order_by("-collected_at")[:LIST_LIMIT]
        )
        serializer = MoodleEngagementSnapshotSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
