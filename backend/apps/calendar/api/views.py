from __future__ import annotations

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditSeverity
from apps.calendar.models import AcademicCalendarEvent, AcademicCalendarEventType, AcademicCalendarStatus
from apps.calendar.services import apply_calendar_filters, record_calendar_audit, visible_calendar_events_for_user

from .serializers import AcademicCalendarEventSerializer


def require_admin(user) -> None:
    if user.primary_role != RoleCode.ADMIN:
        raise PermissionDenied("Admin access is required.")


class AcademicCalendarEventListCreateView(generics.ListCreateAPIView):
    serializer_class = AcademicCalendarEventSerializer

    def get_queryset(self) -> QuerySet[AcademicCalendarEvent]:
        return apply_calendar_filters(visible_calendar_events_for_user(self.request.user), self.request.query_params)

    def perform_create(self, serializer):
        require_admin(self.request.user)
        event = serializer.save(created_by=self.request.user)
        record_calendar_audit(
            actor=self.request.user,
            action="ACADEMIC_CALENDAR_EVENT_CREATED",
            summary=f"Academic calendar event {event.title} was created.",
            event=event,
            severity=AuditSeverity.SUCCESS,
            metadata={
                "eventType": event.event_type,
                "audience": event.audience,
                "priority": event.priority,
                "status": event.status,
                "source": event.source,
            },
            request=self.request,
        )


class AcademicCalendarEventDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AcademicCalendarEventSerializer
    lookup_url_kwarg = "event_id"

    def get_queryset(self) -> QuerySet[AcademicCalendarEvent]:
        return visible_calendar_events_for_user(self.request.user)

    def update(self, request, *args, **kwargs):
        require_admin(request.user)
        response = super().update(request, *args, **kwargs)
        event = self.get_object()
        record_calendar_audit(
            actor=request.user,
            action="ACADEMIC_CALENDAR_EVENT_UPDATED",
            summary=f"Academic calendar event {event.title} was updated.",
            event=event,
            severity=AuditSeverity.INFO,
            metadata={
                "eventType": event.event_type,
                "audience": event.audience,
                "priority": event.priority,
                "status": event.status,
                "source": event.source,
            },
            request=request,
        )
        return response


class AcademicCalendarEventCancelView(APIView):
    def post(self, request, event_id):
        require_admin(request.user)
        event = get_object_or_404(AcademicCalendarEvent.objects.select_related("related_course_section__course"), pk=event_id)
        event.status = AcademicCalendarStatus.CANCELLED
        event.save(update_fields=["status", "updated_at"])
        record_calendar_audit(
            actor=request.user,
            action="ACADEMIC_CALENDAR_EVENT_CANCELLED",
            summary=f"Academic calendar event {event.title} was cancelled.",
            event=event,
            severity=AuditSeverity.WARNING,
            metadata={
                "eventType": event.event_type,
                "audience": event.audience,
                "priority": event.priority,
                "source": event.source,
            },
            request=request,
        )
        return Response(AcademicCalendarEventSerializer(event).data, status=status.HTTP_200_OK)


class AcademicCalendarSummaryView(APIView):
    def get(self, request):
        queryset = visible_calendar_events_for_user(request.user).filter(status=AcademicCalendarStatus.ACTIVE)
        queryset = apply_calendar_filters(queryset, request.query_params)
        now = timezone.now()
        upcoming = queryset.filter(start_at__gte=now).order_by("start_at", "title", "id")
        next_event = upcoming.first()
        current_event = next_event or queryset.order_by("-start_at").first()

        return Response(
            {
                "upcomingCount": upcoming.count(),
                "registrationDeadlines": upcoming.filter(event_type=AcademicCalendarEventType.REGISTRATION_DEADLINE).count(),
                "examPeriods": upcoming.filter(event_type=AcademicCalendarEventType.EXAM_PERIOD).count(),
                "gradeDeadlines": upcoming.filter(event_type=AcademicCalendarEventType.GRADE_SUBMISSION_DEADLINE).count(),
                "currentAcademicYear": current_event.academic_year if current_event else "",
                "currentSemester": current_event.semester if current_event else "",
                "nextEvent": {
                    "id": str(next_event.id),
                    "title": next_event.title,
                    "startAt": AcademicCalendarEventSerializer(next_event).data["startAt"],
                }
                if next_event
                else None,
            },
            status=status.HTTP_200_OK,
        )
