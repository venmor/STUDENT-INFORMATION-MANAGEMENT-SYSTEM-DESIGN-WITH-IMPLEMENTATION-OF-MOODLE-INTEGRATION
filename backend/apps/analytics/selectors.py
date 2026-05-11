from __future__ import annotations

from django.db.models import Avg, Max, Q, QuerySet, Sum

from .models import AnalyticsETLRun, StudentAnalyticsSnapshot


def latest_etl_run() -> AnalyticsETLRun | None:
    return AnalyticsETLRun.objects.order_by("-started_at", "-id").first()


def snapshot_queryset() -> QuerySet[StudentAnalyticsSnapshot]:
    return StudentAnalyticsSnapshot.objects.select_related("student__user", "user", "source_run")


def etl_run_queryset() -> QuerySet[AnalyticsETLRun]:
    return AnalyticsETLRun.objects.all().order_by("-started_at", "-id")


def apply_snapshot_filters(queryset: QuerySet[StudentAnalyticsSnapshot], params) -> QuerySet[StudentAnalyticsSnapshot]:
    student = (params.get("student") or "").strip()
    programme = (params.get("programme") or "").strip()
    academic_year = (params.get("academic_year") or "").strip()
    semester = (params.get("semester") or "").strip()
    search = (params.get("search") or "").strip()
    limit = _safe_limit(params.get("limit"))

    if student:
        queryset = queryset.filter(student_id=student)
    if programme:
        queryset = queryset.filter(programme=programme)
    if academic_year:
        queryset = queryset.filter(academic_year=academic_year)
    if semester:
        queryset = queryset.filter(semester=semester)
    if search:
        queryset = queryset.filter(
            Q(student__student_number__icontains=search)
            | Q(student__user__full_name__icontains=search)
            | Q(student__user__username__icontains=search)
        )

    queryset = queryset.order_by("student__student_number", "academic_year", "semester")
    if limit:
        return queryset[:limit]
    return queryset


def analytics_summary() -> dict:
    snapshots = StudentAnalyticsSnapshot.objects.all()
    latest_run = latest_etl_run()
    aggregate = snapshots.aggregate(
        average_attendance=Avg("attendance_average"),
        official_grade_count=Sum("official_grade_count"),
        financial_flags=Sum("financial_flag_count"),
        latest_moodle_access_at=Max("latest_moodle_access_at"),
    )
    return {
        "latestRun": latest_run,
        "studentsWithSnapshots": snapshots.values("student_id").distinct().count(),
        "moodleSnapshotsUsed": latest_run.moodle_snapshots_used if latest_run else 0,
        "averageAttendance": aggregate["average_attendance"],
        "officialGradeCount": aggregate["official_grade_count"] or 0,
        "financialFlags": aggregate["financial_flags"] or 0,
        "latestMoodleAccessAt": aggregate["latest_moodle_access_at"],
    }


def _safe_limit(raw_value: str | None) -> int | None:
    try:
        limit = int(raw_value or 0)
    except (TypeError, ValueError):
        return None
    if limit <= 0:
        return None
    return min(limit, 200)
