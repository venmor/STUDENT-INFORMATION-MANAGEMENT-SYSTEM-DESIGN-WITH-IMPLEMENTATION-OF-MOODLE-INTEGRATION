from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from apps.accounts.constants import RoleCode
from apps.academics.models import CourseSection, CourseSectionStatus
from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely, sanitize_audit_metadata

from .models import (
    AcademicCalendarAudience,
    AcademicCalendarEvent,
    AcademicCalendarEventType,
    AcademicCalendarPriority,
    AcademicCalendarSource,
    AcademicCalendarStatus,
)


logger = logging.getLogger(__name__)


ROLE_AUDIENCES = {
    RoleCode.STUDENT: [AcademicCalendarAudience.ALL, AcademicCalendarAudience.STUDENTS],
    RoleCode.FACULTY: [AcademicCalendarAudience.ALL, AcademicCalendarAudience.FACULTY],
    RoleCode.ADVISOR: [AcademicCalendarAudience.ALL, AcademicCalendarAudience.ADVISORS],
    RoleCode.ADMIN: list(AcademicCalendarAudience.values),
}


def sanitize_calendar_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    return sanitize_audit_metadata(metadata or {})


def urgency_for_event(event: AcademicCalendarEvent, *, now=None) -> str:
    current = now or timezone.now()
    event_date = timezone.localtime(event.start_at).date()
    today = timezone.localdate(current)
    if event.status == AcademicCalendarStatus.ACTIVE and event_date < today:
        return "OVERDUE"
    if event_date == today:
        return "TODAY"
    if event.start_at <= current + timedelta(days=7):
        return "THIS_WEEK"
    if event.start_at <= current + timedelta(days=30):
        return "UPCOMING"
    return "FUTURE"


def visible_calendar_events_for_user(user) -> QuerySet[AcademicCalendarEvent]:
    queryset = AcademicCalendarEvent.objects.select_related("related_course_section__course", "created_by")
    if getattr(user, "primary_role", None) == RoleCode.ADMIN:
        return queryset
    audiences = ROLE_AUDIENCES.get(getattr(user, "primary_role", None), [])
    return queryset.filter(audience__in=audiences, status=AcademicCalendarStatus.ACTIVE)


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


def month_bounds(raw_value: str | None):
    if not raw_value:
        return None, None
    try:
        year_text, month_text = raw_value.split("-", 1)
        year = int(year_text)
        month = int(month_text)
        if month < 1 or month > 12:
            return None, None
        start = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end = timezone.make_aware(datetime(year + 1, 1, 1))
        else:
            end = timezone.make_aware(datetime(year, month + 1, 1))
        return start, end
    except (TypeError, ValueError):
        return None, None


def apply_calendar_filters(queryset: QuerySet[AcademicCalendarEvent], params) -> QuerySet[AcademicCalendarEvent]:
    event_type = (params.get("event_type") or "").strip().upper()
    audience = (params.get("audience") or "").strip().upper()
    status = (params.get("status") or "").strip().upper()
    semester = (params.get("semester") or "").strip()
    academic_year = (params.get("academic_year") or "").strip()
    month_start, month_end = month_bounds(params.get("month"))
    start = parse_datetime_bound(params.get("start"))
    end = parse_datetime_bound(params.get("end"), end_of_day=True)

    if event_type and event_type != "ALL" and event_type in AcademicCalendarEventType.values:
        queryset = queryset.filter(event_type=event_type)
    if audience and audience != "ALL" and audience in AcademicCalendarAudience.values:
        queryset = queryset.filter(audience=audience)
    if status and status != "ALL" and status in AcademicCalendarStatus.values:
        queryset = queryset.filter(status=status)
    if semester:
        queryset = queryset.filter(semester=semester)
    if academic_year:
        queryset = queryset.filter(academic_year=academic_year)
    if month_start and month_end:
        queryset = queryset.filter(start_at__gte=month_start, start_at__lt=month_end)
    if start:
        queryset = queryset.filter(start_at__gte=start)
    if end:
        queryset = queryset.filter(start_at__lte=end)
    return queryset.order_by("start_at", "title", "id")


def record_calendar_audit(
    *,
    actor=None,
    action: str,
    summary: str,
    event: AcademicCalendarEvent | None = None,
    severity: str = AuditSeverity.INFO,
    metadata: dict[str, Any] | None = None,
    request=None,
):
    record_audit_event_safely(
        actor=actor,
        category=AuditCategory.ACADEMIC_CALENDAR,
        action=action,
        summary=summary,
        target_type="AcademicCalendarEvent" if event is not None else "AcademicCalendar",
        target_id=str(event.id) if event is not None else "bulk-sync",
        severity=severity,
        metadata=sanitize_calendar_metadata(metadata),
        request=request,
    )


def notify_affected_users_for_event(event: AcademicCalendarEvent) -> int:
    if event.status != AcademicCalendarStatus.ACTIVE:
        return 0
    if event.priority not in {AcademicCalendarPriority.HIGH, AcademicCalendarPriority.CRITICAL}:
        return 0

    try:
        from apps.notifications.models import NotificationCategory, NotificationSeverity
        from apps.notifications.services import create_notification
    except Exception:
        logger.exception("Failed to import notification service for calendar event %s", event.id)
        return 0

    role_map = {
        AcademicCalendarAudience.STUDENTS: [RoleCode.STUDENT],
        AcademicCalendarAudience.FACULTY: [RoleCode.FACULTY],
        AcademicCalendarAudience.ADVISORS: [RoleCode.ADVISOR],
        AcademicCalendarAudience.ADMINS: [RoleCode.ADMIN],
        AcademicCalendarAudience.ALL: list(RoleCode.values),
    }
    recipients = get_user_model().objects.filter(primary_role__in=role_map.get(event.audience, []), is_active=True)
    severity = NotificationSeverity.WARNING
    created = 0
    for recipient in recipients:
        create_notification(
            recipient=recipient,
            category=NotificationCategory.ACADEMIC,
            severity=severity,
            title=event.title,
            message=f"{event.title} is scheduled for {timezone.localtime(event.start_at).strftime('%Y-%m-%d %H:%M')}.",
            action_label="Open calendar",
            action_url="/calendar",
            source_type="AcademicCalendarEvent",
            source_id=str(event.id),
            metadata={
                "eventType": event.event_type,
                "audience": event.audience,
                "priority": event.priority,
                "academicYear": event.academic_year,
                "semester": event.semester,
            },
        )
        created += 1
    return created


def _section_event_defaults(section: CourseSection, event_type: str):
    course_label = f"{section.course.course_code} {section.section_code}"
    if event_type == AcademicCalendarEventType.REGISTRATION_OPEN:
        return {
            "title": f"{course_label} registration opens",
            "description": f"Registration opens for {section.course.course_code} {section.section_code}.",
            "start_at": section.registration_opens_at,
            "priority": AcademicCalendarPriority.NORMAL,
        }
    if event_type == AcademicCalendarEventType.REGISTRATION_DEADLINE:
        return {
            "title": f"{course_label} registration deadline",
            "description": f"Last day to register for {section.course.course_code} {section.section_code}.",
            "start_at": section.registration_closes_at,
            "priority": AcademicCalendarPriority.HIGH,
        }
    return {
        "title": f"{course_label} drop/add deadline",
        "description": f"Last day to drop {section.course.course_code} {section.section_code} through the standard registration workflow.",
        "start_at": section.drop_deadline,
        "priority": AcademicCalendarPriority.HIGH,
    }


@dataclass(frozen=True)
class SyncResult:
    created: int
    updated: int


def sync_events_from_course_sections(*, actor=None) -> SyncResult:
    created = 0
    updated = 0
    sections = CourseSection.objects.select_related("course").filter(status=CourseSectionStatus.ACTIVE)
    for section in sections:
        for event_type in (
            AcademicCalendarEventType.REGISTRATION_OPEN,
            AcademicCalendarEventType.REGISTRATION_DEADLINE,
            AcademicCalendarEventType.DROP_DEADLINE,
        ):
            defaults = _section_event_defaults(section, event_type)
            event, was_created = AcademicCalendarEvent.objects.update_or_create(
                source=AcademicCalendarSource.COURSE_SECTION,
                related_course_section=section,
                event_type=event_type,
                defaults={
                    **defaults,
                    "audience": AcademicCalendarAudience.STUDENTS,
                    "academic_year": section.academic_year,
                    "semester": section.semester,
                    "end_at": None,
                    "all_day": False,
                    "location": section.room,
                    "status": AcademicCalendarStatus.ACTIVE,
                    "created_by": actor if getattr(actor, "pk", None) else None,
                    "metadata": sanitize_calendar_metadata(
                        {
                            "source": "course_section",
                            "sectionId": str(section.id),
                            "courseCode": section.course.course_code,
                        }
                    ),
                },
            )
            event.full_clean()
            if was_created:
                created += 1
            else:
                updated += 1

    record_audit_event_safely(
        actor=actor,
        category=AuditCategory.ACADEMIC_CALENDAR,
        action="ACADEMIC_CALENDAR_EVENTS_SYNCED",
        summary=f"Academic calendar course-section sync completed with {created} created and {updated} updated events.",
        target_type="AcademicCalendar",
        target_id="course-section-sync",
        severity=AuditSeverity.INFO,
        metadata={"source": "course_section", "created": created, "updated": updated},
    )
    return SyncResult(created=created, updated=updated)


def seed_demo_events(*, actor=None) -> SyncResult:
    now = timezone.now()
    academic_year = "2026/2027"
    semester = "Semester 1"
    demo_events = [
        ("demo-term-start", "Term Start", AcademicCalendarEventType.TERM_START, AcademicCalendarAudience.ALL, now + timedelta(days=1), AcademicCalendarPriority.NORMAL),
        ("demo-registration-open", "Registration Opens", AcademicCalendarEventType.REGISTRATION_OPEN, AcademicCalendarAudience.STUDENTS, now + timedelta(days=2), AcademicCalendarPriority.NORMAL),
        ("demo-registration-deadline", "Registration Deadline", AcademicCalendarEventType.REGISTRATION_DEADLINE, AcademicCalendarAudience.STUDENTS, now + timedelta(days=14), AcademicCalendarPriority.HIGH),
        ("demo-drop-deadline", "Drop/Add Deadline", AcademicCalendarEventType.DROP_DEADLINE, AcademicCalendarAudience.STUDENTS, now + timedelta(days=28), AcademicCalendarPriority.HIGH),
        ("demo-advising-week", "Advising Week", AcademicCalendarEventType.ADVISING, AcademicCalendarAudience.ADVISORS, now + timedelta(days=7), AcademicCalendarPriority.NORMAL),
        ("demo-exam-period", "Exam Period", AcademicCalendarEventType.EXAM_PERIOD, AcademicCalendarAudience.ALL, now + timedelta(days=75), AcademicCalendarPriority.HIGH),
        ("demo-grade-submission", "Grade Submission Deadline", AcademicCalendarEventType.GRADE_SUBMISSION_DEADLINE, AcademicCalendarAudience.FACULTY, now + timedelta(days=95), AcademicCalendarPriority.CRITICAL),
        ("demo-term-end", "Term End", AcademicCalendarEventType.TERM_END, AcademicCalendarAudience.ALL, now + timedelta(days=90), AcademicCalendarPriority.NORMAL),
    ]

    created = 0
    updated = 0
    for demo_key, title, event_type, audience, start_at, priority in demo_events:
        event, was_created = AcademicCalendarEvent.objects.update_or_create(
            source=AcademicCalendarSource.SYSTEM,
            event_type=event_type,
            title=title,
            academic_year=academic_year,
            semester=semester,
            defaults={
                "description": f"Safe local demo calendar event for {title}.",
                "audience": audience,
                "priority": priority,
                "start_at": start_at,
                "end_at": start_at + timedelta(days=5) if event_type in {AcademicCalendarEventType.ADVISING, AcademicCalendarEventType.EXAM_PERIOD} else None,
                "all_day": event_type in {AcademicCalendarEventType.TERM_START, AcademicCalendarEventType.TERM_END},
                "location": "",
                "status": AcademicCalendarStatus.ACTIVE,
                "created_by": actor if getattr(actor, "pk", None) else None,
                "metadata": sanitize_calendar_metadata({"demo": True, "demoKey": demo_key}),
            },
        )
        event.full_clean()
        if was_created:
            created += 1
        else:
            updated += 1

    if created:
        record_audit_event_safely(
            actor=actor,
            category=AuditCategory.ACADEMIC_CALENDAR,
            action="ACADEMIC_CALENDAR_EVENTS_SYNCED",
            summary=f"Seeded {created} safe Step 3.5D demo academic calendar events.",
            target_type="AcademicCalendar",
            target_id="demo-seed",
            severity=AuditSeverity.INFO,
            metadata={"source": "demo", "created": created, "updated": updated},
        )
    return SyncResult(created=created, updated=updated)
