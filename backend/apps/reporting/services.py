from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Count, Q
from django.utils import timezone

from apps.academics.models import CourseSection, CourseSectionStatus, Enrollment, EnrollmentEvent, EnrollmentStatus, GradeRecord, GradeStatus
from apps.academics.services import calculate_attendance_flags
from apps.audit.models import AuditCategory, AuditEvent, AuditSeverity
from apps.audit.services import sanitize_audit_text
from apps.calendar.models import AcademicCalendarEvent, AcademicCalendarEventType, AcademicCalendarPriority, AcademicCalendarStatus
from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleUserMap,
)
from apps.notifications.models import Notification
from apps.students.models import FinancialFlag, StudentProfile


DEADLINE_EVENT_TYPES = {
    AcademicCalendarEventType.REGISTRATION_DEADLINE,
    AcademicCalendarEventType.DROP_DEADLINE,
    AcademicCalendarEventType.GRADE_SUBMISSION_DEADLINE,
    AcademicCalendarEventType.EXAM_PERIOD,
}


@dataclass(frozen=True, slots=True)
class ReportFilters:
    academic_year: str = ""
    semester: str = ""
    programme: str = ""
    course: str = ""
    status: str = ""

    @classmethod
    def from_params(cls, params) -> "ReportFilters":
        return cls(
            academic_year=(params.get("academic_year") or "").strip(),
            semester=(params.get("semester") or "").strip(),
            programme=(params.get("programme") or "").strip(),
            course=(params.get("course") or "").strip(),
            status=(params.get("status") or "").strip().upper(),
        )

    def as_metadata(self) -> dict[str, str]:
        return {
            "academicYear": self.academic_year,
            "semester": self.semester,
            "programme": self.programme,
            "course": self.course,
            "status": self.status,
        }


def _percentage(numerator: int | Decimal, denominator: int | Decimal) -> float:
    if not denominator:
        return 0
    return round(float(numerator) / float(denominator) * 100, 2)


def _today_bounds():
    start = timezone.make_aware(datetime.combine(timezone.localdate(), time.min))
    return start, start + timedelta(days=1)


def _current_term() -> tuple[str | None, str | None]:
    section = CourseSection.objects.filter(status=CourseSectionStatus.ACTIVE).order_by("-registration_closes_at").first()
    if section is None:
        return None, None
    return section.academic_year, section.semester


def _apply_section_filters(queryset, filters: ReportFilters):
    if filters.academic_year:
        queryset = queryset.filter(academic_year=filters.academic_year)
    if filters.semester:
        queryset = queryset.filter(semester=filters.semester)
    if filters.programme:
        queryset = queryset.filter(course__programme_code__icontains=filters.programme)
    if filters.course:
        queryset = queryset.filter(Q(course__course_code__icontains=filters.course) | Q(course__course_title__icontains=filters.course))
    return queryset


def _base_sections(filters: ReportFilters):
    queryset = CourseSection.objects.select_related("course", "faculty_user").filter(status=CourseSectionStatus.ACTIVE)
    return _apply_section_filters(queryset, filters)


def _base_enrollments(filters: ReportFilters):
    queryset = Enrollment.objects.select_related("student__user", "section__course", "section__faculty_user")
    if filters.academic_year:
        queryset = queryset.filter(section__academic_year=filters.academic_year)
    if filters.semester:
        queryset = queryset.filter(section__semester=filters.semester)
    if filters.programme:
        queryset = queryset.filter(student__programme__icontains=filters.programme)
    if filters.course:
        queryset = queryset.filter(Q(section__course__course_code__icontains=filters.course) | Q(section__course__course_title__icontains=filters.course))
    if filters.status and filters.status != "ALL" and filters.status in EnrollmentStatus.values:
        queryset = queryset.filter(enrollment_status=filters.status)
    return queryset


def _base_grades(filters: ReportFilters):
    queryset = GradeRecord.objects.select_related("student__user", "section__course", "section__faculty_user")
    if filters.academic_year:
        queryset = queryset.filter(section__academic_year=filters.academic_year)
    if filters.semester:
        queryset = queryset.filter(section__semester=filters.semester)
    if filters.programme:
        queryset = queryset.filter(student__programme__icontains=filters.programme)
    if filters.course:
        queryset = queryset.filter(Q(section__course__course_code__icontains=filters.course) | Q(section__course__course_title__icontains=filters.course))
    if filters.status and filters.status != "ALL" and filters.status in GradeStatus.values:
        queryset = queryset.filter(grade_status=filters.status)
    return queryset


def _capacity_status(enrolled: int, capacity: int) -> str:
    if capacity <= 0:
        return "Unavailable"
    fill_rate = _percentage(enrolled, capacity)
    if fill_rate > 100:
        return "Over Capacity"
    if fill_rate == 100:
        return "Full"
    if fill_rate >= 80:
        return "Near Capacity"
    return "Open"


def _capacity_rows(filters: ReportFilters) -> list[dict]:
    sections = _base_sections(filters).annotate(
        enrolled_count=Count(
            "enrollments",
            filter=Q(enrollments__is_active=True, enrollments__enrollment_status=EnrollmentStatus.ENROLLED),
        )
    )
    rows: list[dict] = []
    for section in sections:
        capacity = int(section.max_capacity)
        enrolled = int(section.enrolled_count)
        remaining = max(capacity - enrolled, 0) if capacity > 0 else 0
        fill_rate = _percentage(enrolled, capacity)
        rows.append(
            {
                "sectionId": str(section.id),
                "courseCode": section.course.course_code,
                "courseTitle": section.course.course_title,
                "sectionCode": section.section_code,
                "academicYear": section.academic_year,
                "semester": section.semester,
                "facultyName": section.faculty_user.full_name or section.faculty_user.username,
                "capacity": capacity,
                "enrolledCount": enrolled,
                "remainingSeats": remaining,
                "fillRate": fill_rate,
                "status": _capacity_status(enrolled, capacity),
            }
        )
    return sorted(rows, key=lambda item: (-item["fillRate"], item["courseCode"], item["sectionCode"]))


def _deadline_queryset(filters: ReportFilters):
    now = timezone.now()
    queryset = AcademicCalendarEvent.objects.filter(
        status=AcademicCalendarStatus.ACTIVE,
        event_type__in=DEADLINE_EVENT_TYPES,
        start_at__gte=now,
    ).order_by("start_at", "title")
    if filters.academic_year:
        queryset = queryset.filter(academic_year=filters.academic_year)
    if filters.semester:
        queryset = queryset.filter(semester=filters.semester)
    return queryset


def _event_payload(event: AcademicCalendarEvent | None) -> dict | None:
    if event is None:
        return None
    return {
        "id": str(event.id),
        "title": event.title,
        "eventType": event.event_type,
        "priority": event.priority,
        "academicYear": event.academic_year,
        "semester": event.semester,
        "startAt": event.start_at,
    }


def _latest_engagement_run_payload(run: MoodleEngagementIngestionRun | None) -> dict | None:
    if run is None:
        return None
    return {
        "id": str(run.id),
        "status": run.status,
        "dryRun": run.dry_run,
        "startedAt": run.started_at,
        "completedAt": run.completed_at,
        "coursesInspected": run.courses_inspected,
        "usersInspected": run.users_inspected,
        "snapshotsTotal": run.snapshots_created + run.snapshots_updated,
        "failureCount": run.failure_count,
        "lastError": sanitize_audit_text(run.last_error),
    }


def get_admin_reporting_summary(filters: ReportFilters | None = None) -> dict:
    filters = filters or ReportFilters()
    student_queryset = StudentProfile.objects.all()
    if filters.programme:
        student_queryset = student_queryset.filter(programme__icontains=filters.programme)

    students_total = student_queryset.count()
    students_active = student_queryset.filter(is_active=True).count()
    programme_rows = []
    for row in (
        student_queryset.values("programme")
        .annotate(
            total=Count("id"),
            active=Count("id", filter=Q(is_active=True)),
            inactive=Count("id", filter=Q(is_active=False)),
        )
        .order_by("-total", "programme")
    ):
        programme_rows.append(
            {
                "programme": row["programme"] or "Unspecified",
                "total": row["total"],
                "active": row["active"],
                "inactive": row["inactive"],
                "percentage": _percentage(row["total"], students_total),
            }
        )

    enrollment_queryset = _base_enrollments(filters)
    current_term_queryset = enrollment_queryset
    if not filters.academic_year and not filters.semester:
        year, semester = _current_term()
        if year and semester:
            current_term_queryset = current_term_queryset.filter(section__academic_year=year, section__semester=semester)

    capacity_rows = _capacity_rows(filters)
    grade_queryset = _base_grades(filters)
    active_enrollments = _base_enrollments(filters).filter(is_active=True, enrollment_status=EnrollmentStatus.ENROLLED).count()
    official_grades = grade_queryset.filter(grade_status=GradeStatus.OFFICIAL).count()
    pending_events = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.PENDING).count()
    failed_events = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.FAILED).count()
    processed_events = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.PROCESSED).count()
    latest_run = MoodleEngagementIngestionRun.objects.order_by("-started_at").first()
    deadlines = _deadline_queryset(filters)
    now = timezone.now()
    next_30 = now + timedelta(days=30)
    today_start, today_end = _today_bounds()

    return {
        "students": {
            "total": students_total,
            "active": students_active,
            "inactive": students_total - students_active,
            "byProgramme": programme_rows,
        },
        "enrollments": {
            "total": enrollment_queryset.count(),
            "currentTerm": current_term_queryset.count(),
            "pending": enrollment_queryset.filter(enrollment_status=EnrollmentStatus.WAITLISTED).count(),
            "confirmed": enrollment_queryset.filter(enrollment_status=EnrollmentStatus.ENROLLED).count(),
            "dropped": enrollment_queryset.filter(enrollment_status=EnrollmentStatus.DROPPED).count(),
        },
        "capacity": {
            "sectionsTotal": len(capacity_rows),
            "sectionsNearCapacity": sum(1 for row in capacity_rows if row["status"] == "Near Capacity"),
            "sectionsFull": sum(1 for row in capacity_rows if row["status"] in {"Full", "Over Capacity"}),
            "averageFillRate": round(sum(row["fillRate"] for row in capacity_rows) / len(capacity_rows), 2) if capacity_rows else 0,
        },
        "grades": {
            "draft": grade_queryset.filter(grade_status=GradeStatus.DRAFT).count(),
            "official": official_grades,
            "pendingApproval": 0,
            "completionRate": _percentage(official_grades, active_enrollments),
        },
        "moodle": {
            "pendingEvents": pending_events,
            "failedEvents": failed_events,
            "processedEvents": processed_events,
            "userMappings": MoodleUserMap.objects.count(),
            "courseMappings": MoodleCourseMap.objects.count(),
            "latestEngagementRunStatus": latest_run.status if latest_run else None,
        },
        "calendar": {
            "upcomingDeadlines": deadlines.filter(start_at__lte=next_30).count(),
            "criticalDeadlines": deadlines.filter(start_at__lte=next_30, priority=AcademicCalendarPriority.CRITICAL).count(),
            "nextDeadlineTitle": deadlines.first().title if deadlines.first() else None,
            "nextDeadlineAt": deadlines.first().start_at if deadlines.first() else None,
        },
        "activity": {
            "auditEventsToday": AuditEvent.objects.filter(created_at__gte=today_start, created_at__lt=today_end).count(),
            "unreadAdminNotifications": Notification.objects.filter(recipient__primary_role="ADMIN", is_read=False).count(),
        },
    }


def get_enrollment_report(filters: ReportFilters | None = None) -> dict:
    filters = filters or ReportFilters()
    queryset = _base_enrollments(filters)
    status_rows = [
        {
            "status": value,
            "label": label,
            "count": queryset.filter(enrollment_status=value).count(),
        }
        for value, label in EnrollmentStatus.choices
    ]
    programme_rows = list(
        queryset.values("student__programme")
        .annotate(count=Count("id"))
        .order_by("-count", "student__programme")
    )
    sections = []
    for row in _capacity_rows(filters):
        total_count = queryset.filter(section_id=row["sectionId"]).count()
        sections.append(
            {
                "sectionId": row["sectionId"],
                "courseCode": row["courseCode"],
                "courseTitle": row["courseTitle"],
                "sectionCode": row["sectionCode"],
                "academicYear": row["academicYear"],
                "semester": row["semester"],
                "enrolledCount": row["enrolledCount"],
                "totalEnrollments": total_count,
            }
        )

    recent_events = (
        EnrollmentEvent.objects.filter(enrollment__in=queryset)
        .select_related("enrollment__student__user", "enrollment__section__course", "actor_user")
        .order_by("-created_at")[:10]
    )
    return {
        "filters": filters.as_metadata(),
        "total": queryset.count(),
        "statusBreakdown": status_rows,
        "byProgramme": [
            {
                "programme": row["student__programme"] or "Unspecified",
                "count": row["count"],
            }
            for row in programme_rows
        ],
        "byCourseSection": sections,
        "topSections": sorted(sections, key=lambda item: item["enrolledCount"], reverse=True)[:5],
        "recentActivity": [
            {
                "id": str(event.id),
                "eventType": event.event_type,
                "studentNumber": event.enrollment.student.student_number,
                "studentName": event.enrollment.student.user.full_name or event.enrollment.student.user.username,
                "courseCode": event.enrollment.section.course.course_code,
                "sectionCode": event.enrollment.section.section_code,
                "actor": event.actor_user.full_name if event.actor_user else "System",
                "createdAt": event.created_at,
            }
            for event in recent_events
        ],
    }


def get_capacity_report(filters: ReportFilters | None = None) -> dict:
    filters = filters or ReportFilters()
    rows = _capacity_rows(filters)
    return {
        "filters": filters.as_metadata(),
        "sections": rows,
        "nearOrFullSections": [row for row in rows if row["status"] in {"Near Capacity", "Full", "Over Capacity"}],
        "summary": {
            "sectionsTotal": len(rows),
            "sectionsNearCapacity": sum(1 for row in rows if row["status"] == "Near Capacity"),
            "sectionsFull": sum(1 for row in rows if row["status"] in {"Full", "Over Capacity"}),
            "averageFillRate": round(sum(row["fillRate"] for row in rows) / len(rows), 2) if rows else 0,
        },
    }


def get_grade_report(filters: ReportFilters | None = None) -> dict:
    filters = filters or ReportFilters()
    grade_queryset = _base_grades(filters)
    sections = []
    for section in _base_sections(filters).order_by("course__course_code", "section_code"):
        active_enrolled = Enrollment.objects.filter(section=section, is_active=True, enrollment_status=EnrollmentStatus.ENROLLED).count()
        section_grades = grade_queryset.filter(section=section)
        draft = section_grades.filter(grade_status=GradeStatus.DRAFT).count()
        official = section_grades.filter(grade_status=GradeStatus.OFFICIAL).count()
        submitted = draft + official
        missing = max(active_enrolled - submitted, 0)
        completion_rate = _percentage(official, active_enrolled)
        if active_enrolled == 0:
            section_status = "No Enrollments"
        elif completion_rate == 100:
            section_status = "Complete"
        else:
            section_status = "Needs Review"
        sections.append(
            {
                "sectionId": str(section.id),
                "courseCode": section.course.course_code,
                "courseTitle": section.course.course_title,
                "sectionCode": section.section_code,
                "facultyName": section.faculty_user.full_name or section.faculty_user.username,
                "academicYear": section.academic_year,
                "semester": section.semester,
                "enrolledCount": active_enrolled,
                "draft": draft,
                "official": official,
                "pendingApproval": 0,
                "missingSubmissions": missing,
                "completionRate": completion_rate,
                "status": section_status,
            }
        )

    official = grade_queryset.filter(grade_status=GradeStatus.OFFICIAL).count()
    active_enrollments = _base_enrollments(filters).filter(is_active=True, enrollment_status=EnrollmentStatus.ENROLLED).count()
    return {
        "filters": filters.as_metadata(),
        "totals": {
            "draft": grade_queryset.filter(grade_status=GradeStatus.DRAFT).count(),
            "official": official,
            "pendingApproval": 0,
            "completionRate": _percentage(official, active_enrollments),
            "sectionsWithMissingSubmissions": sum(1 for row in sections if row["missingSubmissions"] > 0),
        },
        "statusBreakdown": [
            {"status": GradeStatus.DRAFT, "label": "Draft", "count": grade_queryset.filter(grade_status=GradeStatus.DRAFT).count()},
            {"status": GradeStatus.OFFICIAL, "label": "Official", "count": official},
        ],
        "sections": sections,
        "sectionsWithMissingSubmissions": [row for row in sections if row["missingSubmissions"] > 0],
    }


def get_moodle_sync_report(filters: ReportFilters | None = None) -> dict:
    latest_failed = IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.FAILED).order_by("-last_attempt_at", "-created_at").first()
    latest_run = MoodleEngagementIngestionRun.objects.order_by("-started_at").first()
    recent_failures = MoodleEngagementIngestionRun.objects.filter(Q(status__in=["FAILED", "PARTIAL"]) | Q(failure_count__gt=0)).order_by("-started_at")[:5]
    return {
        "filters": (filters or ReportFilters()).as_metadata(),
        "outbox": {
            "pending": IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.PENDING).count(),
            "processed": IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.PROCESSED).count(),
            "failed": IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.FAILED).count(),
            "retryable": IntegrationOutboxEvent.objects.filter(status__in=[IntegrationEventStatus.PENDING, IntegrationEventStatus.FAILED]).count(),
        },
        "mappings": {
            "users": MoodleUserMap.objects.count(),
            "courses": MoodleCourseMap.objects.count(),
        },
        "latestFailedEvent": {
            "id": str(latest_failed.id),
            "eventType": latest_failed.event_type,
            "attempts": latest_failed.attempts,
            "lastError": sanitize_audit_text(latest_failed.last_error),
            "lastAttemptAt": latest_failed.last_attempt_at,
            "createdAt": latest_failed.created_at,
        }
        if latest_failed
        else None,
        "latestEngagementRun": _latest_engagement_run_payload(latest_run),
        "recentIngestionFailures": [_latest_engagement_run_payload(run) for run in recent_failures],
    }


def get_calendar_deadline_report(filters: ReportFilters | None = None) -> dict:
    filters = filters or ReportFilters()
    now = timezone.now()
    next_7 = now + timedelta(days=7)
    next_30 = now + timedelta(days=30)
    queryset = _deadline_queryset(filters)
    deadlines = list(queryset.filter(start_at__lte=next_30)[:10])
    return {
        "filters": filters.as_metadata(),
        "upcomingNext7Days": queryset.filter(start_at__lte=next_7).count(),
        "upcomingNext30Days": queryset.filter(start_at__lte=next_30).count(),
        "criticalDeadlines": queryset.filter(start_at__lte=next_30, priority=AcademicCalendarPriority.CRITICAL).count(),
        "highPriorityEvents": queryset.filter(start_at__lte=next_30, priority__in=[AcademicCalendarPriority.HIGH, AcademicCalendarPriority.CRITICAL]).count(),
        "registrationDeadlines": queryset.filter(start_at__lte=next_30, event_type=AcademicCalendarEventType.REGISTRATION_DEADLINE).count(),
        "examPeriods": queryset.filter(start_at__lte=next_30, event_type=AcademicCalendarEventType.EXAM_PERIOD).count(),
        "gradeSubmissionDeadlines": queryset.filter(start_at__lte=next_30, event_type=AcademicCalendarEventType.GRADE_SUBMISSION_DEADLINE).count(),
        "nextDeadline": _event_payload(queryset.first()),
        "deadlines": [_event_payload(event) for event in deadlines],
    }


def _low_attendance_flag_count() -> int:
    count = 0
    for student in StudentProfile.objects.filter(is_active=True).prefetch_related("enrollments"):
        count += len(calculate_attendance_flags(student))
    return count


def _risk_indicators() -> list[dict]:
    capacity_summary = get_capacity_report()["summary"]
    grade_totals = get_grade_report()["totals"]
    calendar_report = get_calendar_deadline_report()
    audit_warnings = AuditEvent.objects.filter(severity=AuditSeverity.WARNING).count()
    audit_errors = AuditEvent.objects.filter(severity=AuditSeverity.ERROR).count()
    indicators = [
        {
            "label": "Failed Moodle sync events",
            "count": IntegrationOutboxEvent.objects.filter(status=IntegrationEventStatus.FAILED).count(),
            "severity": "ERROR",
            "actionUrl": "/admin/moodle-sync",
        },
        {
            "label": "Capacity pressure sections",
            "count": capacity_summary["sectionsNearCapacity"] + capacity_summary["sectionsFull"],
            "severity": "WARNING",
            "actionUrl": "/admin/courses",
        },
        {
            "label": "Sections missing official grades",
            "count": grade_totals["sectionsWithMissingSubmissions"],
            "severity": "WARNING",
            "actionUrl": "/admin/reports",
        },
        {
            "label": "Low attendance flags",
            "count": _low_attendance_flag_count(),
            "severity": "WARNING",
            "actionUrl": "/admin/reports",
        },
        {
            "label": "Active financial flags",
            "count": FinancialFlag.objects.filter(cleared_date__isnull=True).count(),
            "severity": "WARNING",
            "actionUrl": "/admin/reports",
        },
        {
            "label": "Critical academic deadlines",
            "count": calendar_report["criticalDeadlines"],
            "severity": "WARNING",
            "actionUrl": "/calendar",
        },
        {
            "label": "Audit warnings and errors",
            "count": audit_warnings + audit_errors,
            "severity": "WARNING" if audit_errors == 0 else "ERROR",
            "actionUrl": "/admin/audit-log",
        },
    ]
    return indicators


def get_operational_activity_report(filters: ReportFilters | None = None) -> dict:
    today_start, today_end = _today_bounds()
    audit_queryset = AuditEvent.objects.all()
    common_categories = (
        audit_queryset.values("category")
        .annotate(count=Count("id"))
        .order_by("-count", "category")[:8]
    )
    recent_high_severity = audit_queryset.filter(severity__in=[AuditSeverity.WARNING, AuditSeverity.ERROR]).order_by("-created_at")[:8]
    return {
        "filters": (filters or ReportFilters()).as_metadata(),
        "unreadAdminNotifications": Notification.objects.filter(recipient__primary_role="ADMIN", is_read=False).count(),
        "auditEventsToday": audit_queryset.filter(created_at__gte=today_start, created_at__lt=today_end).count(),
        "auditWarnings": audit_queryset.filter(severity=AuditSeverity.WARNING).count(),
        "auditErrors": audit_queryset.filter(severity=AuditSeverity.ERROR).count(),
        "byCategory": {category: audit_queryset.filter(category=category).count() for category in AuditCategory.values},
        "commonCategories": [
            {
                "category": row["category"],
                "count": row["count"],
            }
            for row in common_categories
        ],
        "recentHighSeverityAuditEvents": [
            {
                "id": str(event.id),
                "category": event.category,
                "action": event.action,
                "severity": event.severity,
                "summary": sanitize_audit_text(event.summary),
                "createdAt": event.created_at,
            }
            for event in recent_high_severity
        ],
        "riskIndicators": _risk_indicators(),
    }
