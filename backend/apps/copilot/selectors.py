from __future__ import annotations

from collections import Counter
from typing import Any
from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from apps.academics.models import EnrollmentStatus, GradeStatus
from apps.analytics.models import StudentAnalyticsSnapshot
from apps.calendar.models import AcademicCalendarStatus
from apps.calendar.services import urgency_for_event, visible_calendar_events_for_user
from apps.documents.models import DocumentVisibility
from apps.knowledge.models import KnowledgeChunk
from apps.students.models import StudentProfile

from .models import CopilotMessage, CopilotSession, CopilotSessionStatus
from .safety import bounded_preview


def sessions_for_user(user) -> QuerySet[CopilotSession]:
    return CopilotSession.objects.filter(user=user).select_related("student", "user").prefetch_related("messages")


def active_sessions_for_user(user) -> QuerySet[CopilotSession]:
    return sessions_for_user(user).filter(status=CopilotSessionStatus.ACTIVE)


def messages_for_session(session: CopilotSession) -> QuerySet[CopilotMessage]:
    return session.messages.all().order_by("created_at", "id")


def build_safe_student_context(student: StudentProfile, *, user) -> dict[str, Any]:
    latest_snapshot = (
        StudentAnalyticsSnapshot.objects.filter(student=student)
        .order_by("-updated_at", "-created_at", "-id")
        .first()
    )
    return {
        "fullName": student.user.full_name or student.user.username,
        "studentNumber": student.student_number,
        "programme": student.programme,
        "yearOfStudy": student.year_of_study,
        "academicStanding": student.academic_standing,
        "currentEnrollments": _current_enrollments(student),
        "academicDeadlines": _student_deadlines(user),
        "documentStatusSummary": _student_document_status_summary(student),
        "gradeSummary": _student_grade_summary(student),
        "analyticsSummary": _analytics_summary(latest_snapshot),
    }


def shape_source_references(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_chunk_ids = _existing_uuid_chunk_ids(results)
    references = []
    for row in results:
        chunk_id = str(row.get("chunkId") or "")
        if _is_uuid(chunk_id) and chunk_id not in valid_chunk_ids:
            continue
        references.append(
            {
                "sourceId": str(row.get("sourceId") or ""),
                "chunkId": chunk_id,
                "title": row.get("sourceTitle") or "Institutional source",
                "sourceType": row.get("sourceType") or "OTHER",
                "preview": bounded_preview(row.get("text", ""), limit=260),
                "score": round(float(row.get("score") or 0), 4),
            }
        )
    return references


def _existing_uuid_chunk_ids(results: list[dict[str, Any]]) -> set[str]:
    uuid_values = [str(row.get("chunkId")) for row in results if _is_uuid(str(row.get("chunkId") or ""))]
    if not uuid_values:
        return set()
    return {str(value) for value in KnowledgeChunk.objects.filter(id__in=uuid_values).values_list("id", flat=True)}


def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except (TypeError, ValueError):
        return False


def _current_enrollments(student: StudentProfile) -> list[dict[str, Any]]:
    enrollments = (
        student.enrollments.select_related("section__course")
        .filter(is_active=True, enrollment_status=EnrollmentStatus.ENROLLED)
        .order_by("section__course__course_code", "section__section_code")[:8]
    )
    return [
        {
            "courseCode": enrollment.section.course.course_code,
            "courseTitle": enrollment.section.course.course_title,
            "sectionCode": enrollment.section.section_code,
            "semester": enrollment.section.semester,
            "academicYear": enrollment.section.academic_year,
            "dropDeadline": enrollment.section.drop_deadline.isoformat(),
            "registrationDeadline": enrollment.section.registration_closes_at.isoformat(),
        }
        for enrollment in enrollments
    ]


def _student_deadlines(user) -> list[dict[str, Any]]:
    now = timezone.now()
    events = (
        visible_calendar_events_for_user(user)
        .filter(status=AcademicCalendarStatus.ACTIVE, start_at__gte=now)
        .order_by("start_at", "title")[:8]
    )
    return [
        {
            "title": event.title,
            "eventType": event.event_type,
            "startAt": event.start_at.isoformat(),
            "urgency": urgency_for_event(event, now=now),
        }
        for event in events
    ]


def _student_document_status_summary(student: StudentProfile) -> dict[str, int]:
    documents = student.documents.filter(visibility=DocumentVisibility.STUDENT_VISIBLE)
    counts = Counter(documents.values_list("status", flat=True))
    return {status: counts.get(status, 0) for status in ("PENDING_REVIEW", "APPROVED", "REJECTED", "ARCHIVED")}


def _student_grade_summary(student: StudentProfile) -> dict[str, Any]:
    official_grades = student.grade_records.select_related("section__course").filter(grade_status=GradeStatus.OFFICIAL)
    latest = official_grades.order_by("-officialised_at", "-updated_at")[:5]
    return {
        "officialGradeCount": official_grades.count(),
        "latestOfficialGrades": [
            {
                "courseCode": grade.section.course.course_code,
                "letterGrade": grade.letter_grade,
                "officialisedAt": grade.officialised_at.isoformat() if grade.officialised_at else "",
            }
            for grade in latest
        ],
    }


def _analytics_summary(snapshot: StudentAnalyticsSnapshot | None) -> dict[str, Any]:
    if snapshot is None:
        return {}
    return {
        "academicYear": snapshot.academic_year,
        "semester": snapshot.semester,
        "attendanceAverage": str(snapshot.attendance_average) if snapshot.attendance_average is not None else None,
        "activeEnrollmentCount": snapshot.active_enrollment_count,
        "officialGradeCount": snapshot.official_grade_count,
        "financialFlagCount": snapshot.financial_flag_count,
        "moodleSnapshotCount": snapshot.moodle_snapshot_count,
        "gpa": str(snapshot.gpa) if snapshot.gpa is not None else None,
    }
