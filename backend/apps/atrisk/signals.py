from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Max, Q
from django.utils import timezone

from apps.academics.models import (
    AttendanceRecord,
    AttendanceStatus,
    GradeRecord,
    SpecialGradeCode,
)
from apps.analytics.models import StudentAnalyticsSnapshot
from apps.integration.models import MoodleEngagementSnapshot
from apps.students.models import FinancialFlag, StudentProfile

from .config import SIGNAL_THRESHOLDS


def evaluate_all_signals(student: StudentProfile) -> dict[str, bool]:
    """Evaluate all 9 at-risk signals for a student. Returns dict of signal_name -> bool."""
    return {
        "attendance_flag": _check_attendance_flag(student),
        "academic_probation": _check_academic_probation(student),
        "financial_hold": _check_financial_hold(student),
        "grade_decline": _check_grade_decline(student),
        "incomplete_grade": _check_incomplete_grade(student),
        "moodle_inactivity": _check_moodle_inactivity(student),
        "assignment_miss_rate": _check_assignment_miss_rate(student),
        "quiz_failure_pattern": _check_quiz_failure_pattern(student),
        "forum_disengagement": _check_forum_disengagement(student),
    }


def _check_attendance_flag(student: StudentProfile) -> bool:
    """Returns True if student's attendance is below threshold percentage."""
    threshold = SIGNAL_THRESHOLDS["attendance_flag"]["threshold"]
    records = AttendanceRecord.objects.filter(student=student)
    total = records.count()
    if total == 0:
        return False
    attended = records.filter(
        status__in=[AttendanceStatus.PRESENT, AttendanceStatus.EXCUSED]
    ).count()
    percentage = (Decimal(attended) / Decimal(total)) * Decimal("100")
    return percentage < Decimal(str(threshold))


def _check_academic_probation(student: StudentProfile) -> bool:
    """Returns True if student's academic standing is PROBATION or SUSPENDED."""
    standings = SIGNAL_THRESHOLDS["academic_probation"]["standings"]
    return student.academic_standing in standings


def _check_financial_hold(student: StudentProfile) -> bool:
    """Returns True if student has active (uncleared) financial flags."""
    min_flags = SIGNAL_THRESHOLDS["financial_hold"]["min_flags"]
    active_count = FinancialFlag.objects.filter(
        student=student
    ).filter(
        Q(cleared_date__isnull=True)
    ).count()
    return active_count >= min_flags


def _check_grade_decline(student: StudentProfile) -> bool:
    """Returns True if student's GPA dropped by threshold amount between last two snapshots."""
    gpa_drop = Decimal(str(SIGNAL_THRESHOLDS["grade_decline"]["gpa_drop"]))
    snapshots = list(
        StudentAnalyticsSnapshot.objects.filter(student=student)
        .order_by("-created_at")[:2]
    )
    if len(snapshots) < 2:
        return False
    current = snapshots[0]
    previous = snapshots[1]
    if current.gpa is None or previous.gpa is None:
        return False
    return (previous.gpa - current.gpa) >= gpa_drop


def _check_incomplete_grade(student: StudentProfile) -> bool:
    """Returns True if student has min_incompletes or more incomplete grade records."""
    min_incompletes = SIGNAL_THRESHOLDS["incomplete_grade"]["min_incompletes"]
    count = GradeRecord.objects.filter(
        student=student, special_code=SpecialGradeCode.INCOMPLETE
    ).count()
    return count >= min_incompletes


def _check_moodle_inactivity(student: StudentProfile) -> bool:
    """Returns True if student's last Moodle access is older than configured days."""
    days = SIGNAL_THRESHOLDS["moodle_inactivity"]["days"]
    latest = MoodleEngagementSnapshot.objects.filter(student=student).aggregate(
        latest=Max("moodle_last_access_at")
    )["latest"]
    if latest is None:
        return False
    cutoff = timezone.now() - timedelta(days=days)
    return latest < cutoff


def _check_assignment_miss_rate(student: StudentProfile) -> bool:
    """Returns True if student missed min_missed or more assignments based on Moodle data."""
    min_missed = SIGNAL_THRESHOLDS["assignment_miss_rate"]["min_missed"]
    snapshots = MoodleEngagementSnapshot.objects.filter(student=student)
    for snap in snapshots:
        if snap.assignment_submission_rate is not None and snap.assignment_submission_count is not None:
            count = snap.assignment_submission_count
            rate = float(snap.assignment_submission_rate)
            if rate >= 100 or count == 0:
                continue
            # assignment_submission_count is actual submissions, rate is percentage
            # estimated_total = count / (rate / 100) if rate > 0
            if rate > 0:
                estimated_total = int(count / (rate / 100))
                estimated_missed = estimated_total - count
                if estimated_missed >= min_missed:
                    return True
        # Check raw_summary for missed assignments
        raw = snap.raw_summary or {}
        missed_count = raw.get("assignments_missed", 0)
        if missed_count >= min_missed:
            return True
    return False


def _check_quiz_failure_pattern(student: StudentProfile) -> bool:
    """Returns True if student's average quiz score across courses is below threshold."""
    threshold = Decimal(str(SIGNAL_THRESHOLDS["quiz_failure_pattern"]["threshold"]))
    avg = MoodleEngagementSnapshot.objects.filter(
        student=student, quiz_average__isnull=False, quiz_attempt_count__gt=0
    ).aggregate(overall_avg=Avg("quiz_average"))["overall_avg"]
    if avg is None:
        return False
    return avg < threshold


def _check_forum_disengagement(student: StudentProfile) -> bool:
    """Returns True if student has zero forum posts and course access is older than configured days."""
    days = SIGNAL_THRESHOLDS["forum_disengagement"]["days"]
    snapshots = MoodleEngagementSnapshot.objects.filter(student=student)
    if not snapshots.exists():
        return False
    cutoff = timezone.now() - timedelta(days=days)
    for snap in snapshots:
        if snap.forum_post_count is not None and snap.forum_post_count == 0:
            last_access = snap.moodle_course_last_access_at
            if last_access and last_access < cutoff:
                return True
    return False


# Legacy compatibility mapping
SIGNAL_EVALUATORS = {
    "attendance_flag": lambda s: _check_attendance_flag(s),
    "academic_probation": lambda s: _check_academic_probation(s),
    "financial_hold": lambda s: _check_financial_hold(s),
    "grade_decline": lambda s: _check_grade_decline(s),
    "incomplete_grade": lambda s: _check_incomplete_grade(s),
    "moodle_inactivity": lambda s: _check_moodle_inactivity(s),
    "assignment_miss_rate": lambda s: _check_assignment_miss_rate(s),
    "quiz_failure_pattern": lambda s: _check_quiz_failure_pattern(s),
    "forum_disengagement": lambda s: _check_forum_disengagement(s),
}
