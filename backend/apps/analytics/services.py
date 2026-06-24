from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.db.models import Max, Q
from django.utils import timezone

from apps.academics.models import AttendanceStatus, EnrollmentStatus, GradeStatus
from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely, sanitize_audit_metadata
from apps.integration.models import MoodleEngagementSnapshot
from apps.students.models import StudentProfile

from .models import AnalyticsETLRun, AnalyticsETLRunStatus, StudentAnalyticsSnapshot
from .selectors import analytics_summary


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalyticsETLOptions:
    dry_run: bool = False
    student_id: str | None = None
    academic_year: str = ""
    semester: str = ""
    limit: int | None = None


def run_analytics_etl(
    *,
    dry_run: bool = False,
    student_id=None,
    academic_year: str = "",
    semester: str = "",
    limit: int | None = None,
    actor=None,
    request=None,
) -> AnalyticsETLRun:
    # Analytics snapshots are derived, read-optimized records. They summarize
    # existing SIS and stored Moodle engagement data without becoming the
    # official source for grades, attendance, or student status.
    options = AnalyticsETLOptions(
        dry_run=dry_run,
        student_id=str(student_id) if student_id else None,
        academic_year=academic_year or _default_academic_year(),
        semester=semester or _default_semester(),
        limit=limit,
    )
    run = AnalyticsETLRun.objects.create(
        dry_run=dry_run,
        metadata=sanitize_audit_metadata(
            {
                "studentId": options.student_id,
                "academicYear": options.academic_year,
                "semester": options.semester,
                "limit": options.limit,
            }
        ),
    )
    _record_analytics_audit(
        actor=actor,
        action="ANALYTICS_ETL_RUN_STARTED",
        summary="Analytics ETL run started.",
        run=run,
        request=request,
    )

    students = StudentProfile.objects.select_related("user").filter(is_active=True)
    if student_id:
        students = students.filter(pk=student_id)
    students = students.order_by("student_number")
    if limit:
        students = students[: max(0, limit)]

    last_error = ""
    for student in students:
        try:
            values = build_snapshot_values(student, source_run=run, academic_year=options.academic_year, semester=options.semester)
            run.students_processed += 1
            run.moodle_snapshots_used += values["moodle_snapshot_count"]
            if dry_run:
                continue
            _, created = StudentAnalyticsSnapshot.objects.update_or_create(
                student=student,
                academic_year=options.academic_year,
                semester=options.semester,
                defaults=values,
            )
            if created:
                run.snapshots_created += 1
            else:
                run.snapshots_updated += 1
        except Exception as exc:
            run.failure_count += 1
            last_error = str(exc)
            logger.exception("Analytics ETL failed for student %s", student.id)

    run.last_error = last_error[:2000]
    run.completed_at = timezone.now()
    if run.failure_count and run.students_processed == 0:
        run.status = AnalyticsETLRunStatus.FAILED
    elif run.failure_count:
        run.status = AnalyticsETLRunStatus.PARTIAL
    else:
        run.status = AnalyticsETLRunStatus.SUCCEEDED
    run.save(
        update_fields=[
            "students_processed",
            "snapshots_created",
            "snapshots_updated",
            "moodle_snapshots_used",
            "failure_count",
            "last_error",
            "completed_at",
            "status",
        ]
    )

    _record_analytics_audit(
        actor=actor,
        action="ANALYTICS_ETL_RUN_COMPLETED" if run.status == AnalyticsETLRunStatus.SUCCEEDED else "ANALYTICS_ETL_RUN_FAILED",
        summary=f"Analytics ETL run finished with status {run.status}.",
        run=run,
        severity=AuditSeverity.SUCCESS if run.status == AnalyticsETLRunStatus.SUCCEEDED else AuditSeverity.ERROR,
        request=request,
    )
    if run.failure_count:
        _notify_admins_of_failure(run)
    return run


def build_snapshot_values(
    student: StudentProfile,
    *,
    source_run: AnalyticsETLRun,
    academic_year: str,
    semester: str,
) -> dict[str, Any]:
    moodle = _moodle_engagement_summary(student)
    return {
        "user": student.user,
        "academic_year": academic_year,
        "semester": semester,
        "programme": student.programme,
        "year_of_study": student.year_of_study,
        "academic_standing": student.academic_standing,
        "attendance_average": _attendance_average(student),
        "financial_flag_count": _active_financial_flag_count(student),
        "active_enrollment_count": student.enrollments.filter(is_active=True, enrollment_status=EnrollmentStatus.ENROLLED).count(),
        "draft_grade_count": student.grade_records.filter(grade_status=GradeStatus.DRAFT).count(),
        "official_grade_count": student.grade_records.filter(grade_status=GradeStatus.OFFICIAL).count(),
        "gpa": student.cumulative_gpa,
        "latest_moodle_access_at": moodle["latest_moodle_access_at"],
        "latest_moodle_course_access_at": moodle["latest_moodle_course_access_at"],
        "moodle_snapshot_count": moodle["moodle_snapshot_count"],
        "source_run": source_run,
        "metadata": sanitize_audit_metadata(
            {
                "source": "phase_4_1_analytics_etl",
                "moodleDataSource": "stored_moodle_engagement_snapshots",
                "privacy": "derived_counts_only",
            }
        ),
    }


def get_analytics_summary() -> dict:
    return analytics_summary()


def _attendance_average(student: StudentProfile) -> Decimal | None:
    records = student.attendance_records.all()
    total = records.count()
    if total == 0:
        return None
    attended = records.filter(status__in=[AttendanceStatus.PRESENT, AttendanceStatus.EXCUSED]).count()
    percentage = (Decimal(attended) / Decimal(total)) * Decimal("100")
    return percentage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _active_financial_flag_count(student: StudentProfile) -> int:
    today = timezone.localdate()
    return student.financial_flags.filter(Q(cleared_date__isnull=True) | Q(cleared_date__gt=today)).count()


def _moodle_engagement_summary(student: StudentProfile) -> dict[str, Any]:
    snapshots = MoodleEngagementSnapshot.objects.filter(student=student)
    aggregate = snapshots.aggregate(
        latest_moodle_access_at=Max("moodle_last_access_at"),
        latest_moodle_course_access_at=Max("moodle_course_last_access_at"),
    )
    return {
        "moodle_snapshot_count": snapshots.count(),
        "latest_moodle_access_at": aggregate["latest_moodle_access_at"],
        "latest_moodle_course_access_at": aggregate["latest_moodle_course_access_at"],
    }


def _default_academic_year() -> str:
    today = timezone.localdate()
    return f"{today.year}/{today.year + 1}"


def _default_semester() -> str:
    return "Semester 1"


def _record_analytics_audit(*, actor, action: str, summary: str, run: AnalyticsETLRun, severity=AuditSeverity.INFO, request=None) -> None:
    record_audit_event_safely(
        actor=actor,
        category=AuditCategory.AI,
        action=action,
        summary=summary,
        target_type="AnalyticsETLRun",
        target_id=str(run.id),
        severity=severity,
        metadata={
            "runId": str(run.id),
            "status": run.status,
            "studentsProcessed": run.students_processed,
            "snapshotsCreated": run.snapshots_created,
            "snapshotsUpdated": run.snapshots_updated,
            "moodleSnapshotsUsed": run.moodle_snapshots_used,
            "failureCount": run.failure_count,
            "dryRun": run.dry_run,
        },
        request=request,
    )


def _notify_admins_of_failure(run: AnalyticsETLRun) -> None:
    try:
        from apps.notifications.models import NotificationCategory, NotificationSeverity
        from apps.notifications.services import notify_admins, sanitize_text

        notify_admins(
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.ERROR,
            title="Analytics ETL needs attention",
            message=f"Analytics ETL run {run.id} finished with {run.failure_count} failures. {sanitize_text(run.last_error)[:300]}",
            action_label="Open AI Foundation",
            action_url="/admin/ai-foundation",
            source_type="AnalyticsETLRun",
            source_id=str(run.id),
            metadata={"runId": str(run.id), "status": run.status, "failureCount": run.failure_count},
        )
    except Exception:
        logger.exception("Failed to notify admins about analytics ETL failure %s", run.id)
