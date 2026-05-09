from __future__ import annotations

SIGNAL_THRESHOLDS = {
    "attendance_flag": {"threshold": 75, "weight": "HIGH"},
    "academic_probation": {"standings": ["PROBATION", "SUSPENDED"], "weight": "HIGH"},
    "financial_hold": {"min_flags": 1, "weight": "MEDIUM"},
    "grade_decline": {"gpa_drop": 0.5, "weight": "MEDIUM"},
    "incomplete_grade": {"min_incompletes": 2, "weight": "MEDIUM"},
    "moodle_inactivity": {"days": 14, "weight": "HIGH"},
    "assignment_miss_rate": {"min_missed": 2, "weight": "MEDIUM"},
    "quiz_failure_pattern": {"threshold": 40, "weight": "MEDIUM"},
    "forum_disengagement": {"days": 21, "weight": "LOW"},
}


SIGNAL_DISPLAY_NAMES: dict[str, str] = {
    "attendance_flag": "Low attendance (<{threshold}%)",
    "academic_probation": "Academic probation or suspension",
    "financial_hold": "Active financial hold",
    "grade_decline": "GPA declined by {gpa_drop}+ points",
    "incomplete_grade": "Multiple incomplete grades ({min_incompletes}+)",
    "moodle_inactivity": "No Moodle login in {days}+ days",
    "assignment_miss_rate": "Missed {min_missed}+ assignment deadlines",
    "quiz_failure_pattern": "Average quiz score below {threshold}%",
    "forum_disengagement": "No forum posts in {days}+ days",
}


def get_signal_display(signal_name: str) -> str:
    """Return a human-readable description of a signal using its configured thresholds."""
    template = SIGNAL_DISPLAY_NAMES.get(signal_name, signal_name)
    config = SIGNAL_THRESHOLDS.get(signal_name, {})
    try:
        return template.format(**config)
    except (KeyError, IndexError):
        return template
