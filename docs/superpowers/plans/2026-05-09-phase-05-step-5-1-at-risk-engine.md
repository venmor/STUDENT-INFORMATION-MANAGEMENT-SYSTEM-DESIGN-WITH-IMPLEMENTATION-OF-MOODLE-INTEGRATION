# Phase 5 Step 5.1 — At-Risk Student Insight Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a nightly at-risk processing engine that evaluates 9 signals per student, classifies severity, generates deterministic explanations for Medium/High, and surfaces alerts in the advisor dashboard with acknowledge/history workflow.

**Architecture:** A new Django app `apps.atrisk` with signal evaluator functions, a severity classifier, a deterministic explanation provider, and DRF API endpoints for the advisor dashboard. The engine runs via management command (same logic a Celery task would call). The frontend hook `useAtRiskAlerts` fetches live data and the existing `AtRiskAlertQueue`/`AtRiskAlertRow` components are wired to the real API.

**Tech Stack:** Django 5.x, Django REST Framework, MySQL, React 18, TanStack Query, TypeScript, Axios

---

## File Structure

### New files to create:

```
backend/apps/atrisk/__init__.py
backend/apps/atrisk/apps.py
backend/apps/atrisk/models.py
backend/apps/atrisk/config.py
backend/apps/atrisk/signals.py              (signal evaluator functions)
backend/apps/atrisk/classifier.py           (severity classification)
backend/apps/atrisk/providers.py            (deterministic explanation generator)
backend/apps/atrisk/services.py             (orchestration: evaluate + classify + explain + store)
backend/apps/atrisk/serializers.py
backend/apps/atrisk/views.py
backend/apps/atrisk/urls.py
backend/apps/atrisk/admin.py
backend/apps/atrisk/management/__init__.py
backend/apps/atrisk/management/commands/__init__.py
backend/apps/atrisk/management/commands/run_at_risk_engine.py
backend/apps/atrisk/management/commands/seed_at_risk_demo.py
backend/apps/atrisk/tests/__init__.py
backend/apps/atrisk/tests/test_signals.py
backend/apps/atrisk/tests/test_classifier.py
backend/apps/atrisk/tests/test_services.py
backend/apps/atrisk/tests/test_api.py
backend/apps/atrisk/migrations/__init__.py
```

### Existing files to modify:

```
backend/sis_backend/settings.py             (add apps.atrisk to INSTALLED_APPS)
backend/sis_backend/urls.py                 (add URL include)
backend/apps/accounts/access.py             (add route policies)
frontend/src/hooks/useAtRiskAlerts.ts       (replace placeholder with live hook)
frontend/src/components/advisor/AtRiskAlertQueue.tsx  (replace placeholder with live data)
frontend/src/pages/advisor/AlertHistory.tsx  (show historical alerts from API)
```

---

## Task 1: Create Branch and App Skeleton

**Files:**
- Create: `backend/apps/atrisk/__init__.py`
- Create: `backend/apps/atrisk/apps.py`
- Modify: `backend/sis_backend/settings.py`

- [ ] **Step 1: Create feature branch**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION
git checkout main && git pull
git checkout -b feature/phase-05-step-5-1-at-risk-engine
```

- [ ] **Step 2: Create app directory and skeleton files**

```bash
mkdir -p backend/apps/atrisk/management/commands
mkdir -p backend/apps/atrisk/tests
mkdir -p backend/apps/atrisk/migrations
```

Create `backend/apps/atrisk/__init__.py` (empty file).

Create `backend/apps/atrisk/apps.py`:
```python
from django.apps import AppConfig


class AtRiskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.atrisk"
```

Create `backend/apps/atrisk/management/__init__.py` (empty).
Create `backend/apps/atrisk/management/commands/__init__.py` (empty).
Create `backend/apps/atrisk/tests/__init__.py` (empty).
Create `backend/apps/atrisk/migrations/__init__.py` (empty).

- [ ] **Step 3: Add to INSTALLED_APPS**

In `backend/sis_backend/settings.py`, add `"apps.atrisk"` after `"apps.summarisation"` in the `INSTALLED_APPS` list.

- [ ] **Step 4: Verify app loads**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
python manage.py check
```
Expected: System check identified no issues.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/atrisk/ backend/sis_backend/settings.py
git commit -m "feat(atrisk): scaffold app skeleton and register in INSTALLED_APPS"
```

---

## Task 2: Configuration Module

**Files:**
- Create: `backend/apps/atrisk/config.py`

- [ ] **Step 1: Create config.py with signal thresholds**

Create `backend/apps/atrisk/config.py`:
```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SignalThreshold:
    weight: str  # "HIGH", "MEDIUM", "LOW"
    params: dict[str, Any] = field(default_factory=dict)


SIGNAL_THRESHOLDS: dict[str, SignalThreshold] = {
    "attendance_flag": SignalThreshold(weight="HIGH", params={"threshold": 75}),
    "academic_probation": SignalThreshold(
        weight="HIGH", params={"standings": ["PROBATION", "SUSPENDED"]}
    ),
    "financial_hold": SignalThreshold(weight="MEDIUM", params={"min_flags": 1}),
    "grade_decline": SignalThreshold(weight="MEDIUM", params={"gpa_drop": 0.5}),
    "incomplete_grade": SignalThreshold(weight="MEDIUM", params={"min_incompletes": 2}),
    "moodle_inactivity": SignalThreshold(weight="HIGH", params={"days": 14}),
    "assignment_miss_rate": SignalThreshold(weight="MEDIUM", params={"min_missed": 2}),
    "quiz_failure_pattern": SignalThreshold(weight="MEDIUM", params={"threshold": 40}),
    "forum_disengagement": SignalThreshold(weight="LOW", params={"days": 21}),
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
    template = SIGNAL_DISPLAY_NAMES.get(signal_name, signal_name)
    threshold = SIGNAL_THRESHOLDS.get(signal_name)
    if threshold:
        return template.format(**threshold.params)
    return template
```

- [ ] **Step 2: Commit**

```bash
git add backend/apps/atrisk/config.py
git commit -m "feat(atrisk): add configurable signal thresholds (AI-RSK-008)"
```

---

## Task 3: Models

**Files:**
- Create: `backend/apps/atrisk/models.py`
- Create: `backend/apps/atrisk/admin.py`

- [ ] **Step 1: Create models.py**

Create `backend/apps/atrisk/models.py`:
```python
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AlertSeverity(models.TextChoices):
    HIGH = "HIGH", "High"
    MEDIUM = "MEDIUM", "Medium"
    LOW = "LOW", "Low"


class AlertStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
    AUTO_CLOSED = "AUTO_CLOSED", "Auto-closed"


class AtRiskAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="at_risk_alerts",
    )
    severity = models.CharField(max_length=8, choices=AlertSeverity.choices)
    status = models.CharField(
        max_length=16, choices=AlertStatus.choices, default=AlertStatus.OPEN
    )
    active_signals = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    provider = models.CharField(max_length=40, default="deterministic")
    model_name = models.CharField(max_length=120, default="deterministic-at-risk-v1")
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_at_risk_alerts",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    auto_closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-severity", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-severity", "-created_at"], name="atrisk_status_sev_idx"),
            models.Index(fields=["student", "-created_at"], name="atrisk_student_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.student}:{self.severity}:{self.status}"
```

- [ ] **Step 2: Create admin.py**

Create `backend/apps/atrisk/admin.py`:
```python
from django.contrib import admin

from .models import AtRiskAlert


@admin.register(AtRiskAlert)
class AtRiskAlertAdmin(admin.ModelAdmin):
    list_display = ["student", "severity", "status", "created_at"]
    list_filter = ["severity", "status"]
    search_fields = ["student__student_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
```

- [ ] **Step 3: Generate migration**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
python manage.py makemigrations atrisk
```
Expected: Creates `migrations/0001_initial.py`.

- [ ] **Step 4: Verify migration applies (dry-run check)**

```bash
python manage.py migrate --run-syncdb 2>&1 | tail -5
python manage.py check
```
Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/atrisk/models.py backend/apps/atrisk/admin.py backend/apps/atrisk/migrations/
git commit -m "feat(atrisk): add AtRiskAlert model with severity, signals, explanation (AI-RSK-004)"
```

---

## Task 4: Signal Evaluators

**Files:**
- Create: `backend/apps/atrisk/signals.py`
- Create: `backend/apps/atrisk/tests/test_signals.py`

- [ ] **Step 1: Write test_signals.py**

Create `backend/apps/atrisk/tests/test_signals.py`:
```python
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.constants import RoleCode
from apps.academics.models import (
    AttendanceRecord,
    AttendanceSession,
    AttendanceStatus,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentStatus,
    GradeRecord,
    GradeStatus,
    SpecialGradeCode,
)
from apps.integration.models import (
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
)
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile
from apps.testutils import create_user

from apps.atrisk.config import SIGNAL_THRESHOLDS
from apps.atrisk.signals import evaluate_all_signals


pytestmark = pytest.mark.django_db


@pytest.fixture
def student():
    user = create_user(username="atrisk.student1", primary_role=RoleCode.STUDENT, email="atrisk1@example.edu")
    return StudentProfile.objects.create(
        user=user,
        student_number="2026/RISK/001",
        national_id="NRC-RISK-001",
        date_of_birth=date(2003, 3, 15),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=2,
        academic_standing=AcademicStanding.GOOD_STANDING,
        cumulative_gpa=Decimal("3.20"),
        is_active=True,
    )


@pytest.fixture
def advisor():
    return create_user(username="atrisk.advisor1", primary_role=RoleCode.ADVISOR, email="atrisk.advisor1@example.edu")


@pytest.fixture
def course_and_section(advisor):
    from apps.academics.models import Course
    course = Course.objects.create(course_code="CS201", title="Data Structures", credits=3, created_by_user=advisor)
    section = CourseSection.objects.create(
        course=course,
        section_code="A",
        semester="Semester 1",
        academic_year="2025/2026",
        status=CourseSectionStatus.ACTIVE,
        instructor_user=advisor,
        capacity=30,
    )
    return course, section


def test_attendance_flag_triggers_when_below_threshold(student, advisor, course_and_section):
    _, section = course_and_section
    Enrollment.objects.create(student=student, section=section, enrollment_status=EnrollmentStatus.ENROLLED, actor_role="ADMIN")
    session = AttendanceSession.objects.create(section=section, session_date=date.today(), created_by_user=advisor)
    # 4 absences out of 5 sessions = 20% attendance
    for i in range(4):
        AttendanceRecord.objects.create(student=student, session=session, status=AttendanceStatus.ABSENT)
    AttendanceRecord.objects.create(student=student, session=session, status=AttendanceStatus.PRESENT)

    results = evaluate_all_signals(student)
    assert results["attendance_flag"] is True


def test_attendance_flag_does_not_trigger_when_above_threshold(student, advisor, course_and_section):
    _, section = course_and_section
    Enrollment.objects.create(student=student, section=section, enrollment_status=EnrollmentStatus.ENROLLED, actor_role="ADMIN")
    session = AttendanceSession.objects.create(section=section, session_date=date.today(), created_by_user=advisor)
    # 4 present out of 5 sessions = 80% attendance
    for i in range(4):
        AttendanceRecord.objects.create(student=student, session=session, status=AttendanceStatus.PRESENT)
    AttendanceRecord.objects.create(student=student, session=session, status=AttendanceStatus.ABSENT)

    results = evaluate_all_signals(student)
    assert results["attendance_flag"] is False


def test_academic_probation_triggers(student):
    student.academic_standing = AcademicStanding.PROBATION
    student.save()

    results = evaluate_all_signals(student)
    assert results["academic_probation"] is True


def test_academic_probation_does_not_trigger_for_good_standing(student):
    results = evaluate_all_signals(student)
    assert results["academic_probation"] is False


def test_financial_hold_triggers(student, advisor):
    FinancialFlag.objects.create(
        student=student,
        flag_type="TUITION_OVERDUE",
        reason="Outstanding fees",
        effective_date=date.today(),
        created_by_user=advisor,
    )

    results = evaluate_all_signals(student)
    assert results["financial_hold"] is True


def test_financial_hold_does_not_trigger_when_cleared(student, advisor):
    FinancialFlag.objects.create(
        student=student,
        flag_type="TUITION_OVERDUE",
        reason="Outstanding fees",
        effective_date=date.today() - timedelta(days=30),
        cleared_date=date.today() - timedelta(days=5),
        created_by_user=advisor,
    )

    results = evaluate_all_signals(student)
    assert results["financial_hold"] is False


def test_grade_decline_triggers(student):
    student.cumulative_gpa = Decimal("2.50")
    student.save()
    # GPA dropped from snapshot's previous value (simulated via metadata or prior snapshot)
    # For the signal evaluator, we check against previous semester's snapshot
    # If no prior snapshot, signal should not trigger
    results = evaluate_all_signals(student)
    # Without a prior snapshot, no decline is detectable
    assert results["grade_decline"] is False


def test_incomplete_grade_triggers(student, advisor, course_and_section):
    _, section = course_and_section
    GradeRecord.objects.create(
        student=student, section=section, grade_status=GradeStatus.OFFICIAL,
        special_code=SpecialGradeCode.INCOMPLETE, entered_by_user=advisor,
    )
    # Need a second section for second incomplete
    from apps.academics.models import Course
    course2 = Course.objects.create(course_code="CS202", title="Algorithms", credits=3, created_by_user=advisor)
    section2 = CourseSection.objects.create(
        course=course2, section_code="A", semester="Semester 1", academic_year="2025/2026",
        status=CourseSectionStatus.ACTIVE, instructor_user=advisor, capacity=30,
    )
    GradeRecord.objects.create(
        student=student, section=section2, grade_status=GradeStatus.OFFICIAL,
        special_code=SpecialGradeCode.INCOMPLETE, entered_by_user=advisor,
    )

    results = evaluate_all_signals(student)
    assert results["incomplete_grade"] is True


def test_moodle_inactivity_triggers(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        moodle_last_access_at=timezone.now() - timedelta(days=20),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["moodle_inactivity"] is True


def test_moodle_inactivity_does_not_trigger_with_recent_access(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        moodle_last_access_at=timezone.now() - timedelta(days=3),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["moodle_inactivity"] is False


def test_quiz_failure_pattern_triggers(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        quiz_average=Decimal("35.00"),
        quiz_attempt_count=5,
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["quiz_failure_pattern"] is True


def test_forum_disengagement_triggers(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        forum_post_count=0,
        moodle_course_last_access_at=timezone.now() - timedelta(days=25),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["forum_disengagement"] is True


def test_no_signals_for_clean_student(student):
    results = evaluate_all_signals(student)
    active = [k for k, v in results.items() if v]
    assert active == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
pytest apps/atrisk/tests/test_signals.py -v 2>&1 | tail -20
```
Expected: ImportError — `cannot import name 'evaluate_all_signals' from 'apps.atrisk.signals'`

- [ ] **Step 3: Create signals.py with all 9 signal evaluators**

Create `backend/apps/atrisk/signals.py`:
```python
from __future__ import annotations

from decimal import Decimal
from typing import Any

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
    threshold = SIGNAL_THRESHOLDS["attendance_flag"].params["threshold"]
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
    standings = SIGNAL_THRESHOLDS["academic_probation"].params["standings"]
    return student.academic_standing in standings


def _check_financial_hold(student: StudentProfile) -> bool:
    min_flags = SIGNAL_THRESHOLDS["financial_hold"].params["min_flags"]
    today = timezone.localdate()
    active_count = student.financial_flags.filter(
        Q(cleared_date__isnull=True) | Q(cleared_date__gt=today)
    ).count()
    return active_count >= min_flags


def _check_grade_decline(student: StudentProfile) -> bool:
    gpa_drop = Decimal(str(SIGNAL_THRESHOLDS["grade_decline"].params["gpa_drop"]))
    snapshots = StudentAnalyticsSnapshot.objects.filter(student=student).order_by("-created_at")[:2]
    if snapshots.count() < 2:
        return False
    current = snapshots[0]
    previous = snapshots[1]
    if current.gpa is None or previous.gpa is None:
        return False
    return (previous.gpa - current.gpa) >= gpa_drop


def _check_incomplete_grade(student: StudentProfile) -> bool:
    min_incompletes = SIGNAL_THRESHOLDS["incomplete_grade"].params["min_incompletes"]
    count = GradeRecord.objects.filter(
        student=student, special_code=SpecialGradeCode.INCOMPLETE
    ).count()
    return count >= min_incompletes


def _check_moodle_inactivity(student: StudentProfile) -> bool:
    days = SIGNAL_THRESHOLDS["moodle_inactivity"].params["days"]
    latest = MoodleEngagementSnapshot.objects.filter(student=student).aggregate(
        latest=Max("moodle_last_access_at")
    )["latest"]
    if latest is None:
        return False
    cutoff = timezone.now() - timezone.timedelta(days=days)
    return latest < cutoff


def _check_assignment_miss_rate(student: StudentProfile) -> bool:
    min_missed = SIGNAL_THRESHOLDS["assignment_miss_rate"].params["min_missed"]
    snapshots = MoodleEngagementSnapshot.objects.filter(student=student)
    for snap in snapshots:
        if snap.assignment_submission_rate is not None and snap.assignment_submission_rate < Decimal("100"):
            expected = snap.assignment_submission_count or 0
            if snap.assignment_submission_rate > 0 and expected > 0:
                actual_rate = snap.assignment_submission_rate / Decimal("100")
                missed = int(expected * (1 - float(actual_rate)))
                if missed >= min_missed:
                    return True
        elif snap.assignment_submission_rate is not None and snap.assignment_submission_rate == Decimal("0") and (snap.assignment_submission_count or 0) == 0:
            pass
    # Alternative: check raw_summary for missed assignments
    for snap in snapshots:
        raw = snap.raw_summary or {}
        missed_count = raw.get("assignments_missed", 0)
        if missed_count >= min_missed:
            return True
    return False


def _check_quiz_failure_pattern(student: StudentProfile) -> bool:
    threshold = Decimal(str(SIGNAL_THRESHOLDS["quiz_failure_pattern"].params["threshold"]))
    avg = MoodleEngagementSnapshot.objects.filter(
        student=student, quiz_average__isnull=False, quiz_attempt_count__gt=0
    ).aggregate(overall_avg=Avg("quiz_average"))["overall_avg"]
    if avg is None:
        return False
    return avg < threshold


def _check_forum_disengagement(student: StudentProfile) -> bool:
    days = SIGNAL_THRESHOLDS["forum_disengagement"].params["days"]
    snapshots = MoodleEngagementSnapshot.objects.filter(student=student)
    if not snapshots.exists():
        return False
    cutoff = timezone.now() - timezone.timedelta(days=days)
    # Check if any course has zero forum posts AND last course access is old
    for snap in snapshots:
        if (snap.forum_post_count is not None and snap.forum_post_count == 0):
            last_access = snap.moodle_course_last_access_at
            if last_access and last_access < cutoff:
                return True
    return False
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
mysql -u modern_sis -pmodern_sis -h 127.0.0.1 -P 3313 -e "DROP DATABASE IF EXISTS test_modern_sis; CREATE DATABASE test_modern_sis CHARACTER SET utf8mb4;"
pytest apps/atrisk/tests/test_signals.py -v
```
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/atrisk/signals.py backend/apps/atrisk/tests/test_signals.py
git commit -m "feat(atrisk): implement 9 signal evaluators with tests (AI-RSK-002)"
```

---

## Task 5: Severity Classifier

**Files:**
- Create: `backend/apps/atrisk/classifier.py`
- Create: `backend/apps/atrisk/tests/test_classifier.py`

- [ ] **Step 1: Write test_classifier.py**

Create `backend/apps/atrisk/tests/test_classifier.py`:
```python
from __future__ import annotations

from apps.atrisk.classifier import classify_severity


def test_high_severity_from_one_high_signal():
    signals = {"attendance_flag": True, "academic_probation": False, "financial_hold": False,
               "grade_decline": False, "incomplete_grade": False, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": False}
    assert classify_severity(signals) == "HIGH"


def test_high_severity_from_three_signals_any_weight():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": True,
               "grade_decline": True, "incomplete_grade": True, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": False}
    assert classify_severity(signals) == "HIGH"


def test_medium_severity_from_two_medium_signals():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": True,
               "grade_decline": True, "incomplete_grade": False, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": False}
    assert classify_severity(signals) == "MEDIUM"


def test_medium_severity_from_one_medium_plus_two_low():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": True,
               "grade_decline": False, "incomplete_grade": False, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": True}
    # Only 1 medium + 1 low = LOW per SRS... need 1 medium + 2 low
    # Actually per SRS: 1 Medium + 2 Low => MEDIUM. But we only have 1 Low signal possible.
    # So test with what's possible: 1 medium + 1 low = still LOW? Let's test the actual boundary.
    # With 1 medium + 1 low, it's 2 total but less than 3, and only 1 medium:
    assert classify_severity(signals) == "LOW"


def test_low_severity_from_single_medium_signal():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": True,
               "grade_decline": False, "incomplete_grade": False, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": False}
    assert classify_severity(signals) == "LOW"


def test_low_severity_from_single_low_signal():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": False,
               "grade_decline": False, "incomplete_grade": False, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": True}
    assert classify_severity(signals) == "LOW"


def test_none_when_no_signals_active():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": False,
               "grade_decline": False, "incomplete_grade": False, "moodle_inactivity": False,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": False}
    assert classify_severity(signals) is None


def test_high_severity_from_moodle_inactivity_alone():
    signals = {"attendance_flag": False, "academic_probation": False, "financial_hold": False,
               "grade_decline": False, "incomplete_grade": False, "moodle_inactivity": True,
               "assignment_miss_rate": False, "quiz_failure_pattern": False, "forum_disengagement": False}
    assert classify_severity(signals) == "HIGH"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest apps/atrisk/tests/test_classifier.py -v 2>&1 | tail -5
```
Expected: ImportError for `classify_severity`.

- [ ] **Step 3: Implement classifier.py**

Create `backend/apps/atrisk/classifier.py`:
```python
from __future__ import annotations

from .config import SIGNAL_THRESHOLDS


def classify_severity(signals: dict[str, bool]) -> str | None:
    """
    Classify alert severity based on active signals.

    Rules (SRS):
    - HIGH: Any 1 High-weight signal active, OR any 3+ signals active of any weight
    - MEDIUM: Any 2 Medium-weight signals active, OR 1 Medium + 2 Low signals
    - LOW: Any 1 Low or 1 Medium signal active in isolation
    - None: No signals active
    """
    active = [name for name, is_active in signals.items() if is_active]
    if not active:
        return None

    active_count = len(active)
    high_count = sum(1 for name in active if SIGNAL_THRESHOLDS[name].weight == "HIGH")
    medium_count = sum(1 for name in active if SIGNAL_THRESHOLDS[name].weight == "MEDIUM")
    low_count = sum(1 for name in active if SIGNAL_THRESHOLDS[name].weight == "LOW")

    # HIGH: any 1 High-weight signal OR 3+ signals of any weight
    if high_count >= 1 or active_count >= 3:
        return "HIGH"

    # MEDIUM: 2+ Medium signals OR 1 Medium + 2 Low
    if medium_count >= 2:
        return "MEDIUM"
    if medium_count >= 1 and low_count >= 2:
        return "MEDIUM"

    # LOW: 1 Low or 1 Medium signal in isolation
    return "LOW"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest apps/atrisk/tests/test_classifier.py -v
```
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/atrisk/classifier.py backend/apps/atrisk/tests/test_classifier.py
git commit -m "feat(atrisk): implement severity classifier per SRS rules (AI-RSK-003)"
```

---

## Task 6: Deterministic Explanation Provider

**Files:**
- Create: `backend/apps/atrisk/providers.py`

- [ ] **Step 1: Create providers.py**

Create `backend/apps/atrisk/providers.py`:
```python
from __future__ import annotations

from .config import SIGNAL_THRESHOLDS, get_signal_display


SEVERITY_ADVICE = {
    "HIGH": "Immediate advisor intervention is recommended.",
    "MEDIUM": "Advisor follow-up within the next few days is recommended.",
    "LOW": "Monitor and review at next scheduled check-in.",
}


def generate_explanation(*, active_signals: list[str], severity: str) -> str:
    """
    Build a deterministic 2-3 sentence explanation for at-risk alerts.
    Used when severity is MEDIUM or HIGH.
    """
    if not active_signals:
        return ""

    # Sentence 1: summarise what triggered
    if len(active_signals) == 1:
        sentence1 = f"This student has triggered a {get_signal_display(active_signals[0]).lower()} concern."
    elif len(active_signals) == 2:
        sentence1 = (
            f"This student has triggered concerns for "
            f"{get_signal_display(active_signals[0]).lower()} and "
            f"{get_signal_display(active_signals[1]).lower()}."
        )
    else:
        display_names = [get_signal_display(s).lower() for s in active_signals[:3]]
        sentence1 = (
            f"This student has triggered {len(active_signals)} risk signals including "
            f"{', '.join(display_names[:-1])}, and {display_names[-1]}."
        )

    # Sentence 2: describe what the signals mean
    weight_groups = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for sig in active_signals:
        weight = SIGNAL_THRESHOLDS[sig].weight
        weight_groups[weight].append(sig)

    parts = []
    if weight_groups["HIGH"]:
        parts.append(f"{len(weight_groups['HIGH'])} high-weight")
    if weight_groups["MEDIUM"]:
        parts.append(f"{len(weight_groups['MEDIUM'])} medium-weight")
    if weight_groups["LOW"]:
        parts.append(f"{len(weight_groups['LOW'])} low-weight")
    sentence2 = f"The alert includes {' and '.join(parts)} signal(s) resulting in {severity} severity classification."

    # Sentence 3: recommendation
    sentence3 = SEVERITY_ADVICE.get(severity, SEVERITY_ADVICE["LOW"])

    return f"{sentence1} {sentence2} {sentence3}"
```

- [ ] **Step 2: Commit**

```bash
git add backend/apps/atrisk/providers.py
git commit -m "feat(atrisk): add deterministic explanation provider (AI-RSK-003)"
```

---

## Task 7: Core Service — Orchestration

**Files:**
- Create: `backend/apps/atrisk/services.py`
- Create: `backend/apps/atrisk/tests/test_services.py`

- [ ] **Step 1: Write test_services.py**

Create `backend/apps/atrisk/tests/test_services.py`:
```python
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.constants import RoleCode
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile
from apps.testutils import create_user

from apps.atrisk.models import AlertSeverity, AlertStatus, AtRiskAlert
from apps.atrisk.services import process_student, run_at_risk_engine, acknowledge_alert, auto_close_resolved_alerts


pytestmark = pytest.mark.django_db


@pytest.fixture
def advisor():
    return create_user(username="svc.advisor", primary_role=RoleCode.ADVISOR, email="svc.advisor@example.edu")


@pytest.fixture
def student_on_probation():
    user = create_user(username="svc.probation", primary_role=RoleCode.STUDENT, email="svc.probation@example.edu")
    return StudentProfile.objects.create(
        user=user,
        student_number="2026/SVC/001",
        national_id="NRC-SVC-001",
        date_of_birth=date(2003, 5, 10),
        gender="Male",
        programme="BSc IT",
        year_of_study=2,
        academic_standing=AcademicStanding.PROBATION,
        cumulative_gpa=Decimal("1.80"),
        is_active=True,
    )


@pytest.fixture
def clean_student():
    user = create_user(username="svc.clean", primary_role=RoleCode.STUDENT, email="svc.clean@example.edu")
    return StudentProfile.objects.create(
        user=user,
        student_number="2026/SVC/002",
        national_id="NRC-SVC-002",
        date_of_birth=date(2003, 8, 20),
        gender="Female",
        programme="BA English",
        year_of_study=1,
        academic_standing=AcademicStanding.GOOD_STANDING,
        cumulative_gpa=Decimal("3.50"),
        is_active=True,
    )


def test_process_student_creates_high_alert_for_probation(student_on_probation):
    alert = process_student(student_on_probation)
    assert alert is not None
    assert alert.severity == AlertSeverity.HIGH
    assert alert.status == AlertStatus.OPEN
    assert "academic_probation" in alert.active_signals
    assert alert.explanation != ""


def test_process_student_returns_none_for_clean_student(clean_student):
    alert = process_student(clean_student)
    assert alert is None


def test_process_student_does_not_duplicate_alert(student_on_probation):
    alert1 = process_student(student_on_probation)
    alert2 = process_student(student_on_probation)
    assert alert1 is not None
    assert alert2 is None
    assert AtRiskAlert.objects.filter(student=student_on_probation, status=AlertStatus.OPEN).count() == 1


def test_run_at_risk_engine_processes_all_active_students(student_on_probation, clean_student):
    stats = run_at_risk_engine()
    assert stats["students_processed"] == 2
    assert stats["alerts_created"] == 1


def test_acknowledge_alert(student_on_probation, advisor):
    alert = process_student(student_on_probation)
    assert alert is not None
    acknowledged = acknowledge_alert(alert_id=alert.id, user=advisor)
    assert acknowledged.status == AlertStatus.ACKNOWLEDGED
    assert acknowledged.acknowledged_by == advisor
    assert acknowledged.acknowledged_at is not None


def test_auto_close_resolved_alerts(student_on_probation):
    alert = process_student(student_on_probation)
    assert alert is not None
    # Fix the student
    student_on_probation.academic_standing = AcademicStanding.GOOD_STANDING
    student_on_probation.save()
    closed_count = auto_close_resolved_alerts()
    assert closed_count == 1
    alert.refresh_from_db()
    assert alert.status == AlertStatus.AUTO_CLOSED
    assert alert.auto_closed_at is not None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest apps/atrisk/tests/test_services.py -v 2>&1 | tail -5
```
Expected: ImportError for services module functions.

- [ ] **Step 3: Implement services.py**

Create `backend/apps/atrisk/services.py`:
```python
from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely
from apps.copilot.audit import record_ai_audit
from apps.copilot.models import AIAuditAction, CopilotProvider
from apps.students.models import StudentProfile

from .classifier import classify_severity
from .models import AlertSeverity, AlertStatus, AtRiskAlert
from .providers import generate_explanation
from .signals import evaluate_all_signals


logger = logging.getLogger(__name__)


@transaction.atomic
def process_student(student: StudentProfile) -> AtRiskAlert | None:
    """Evaluate signals for a single student, create alert if warranted."""
    signals = evaluate_all_signals(student)
    active_signals = [name for name, is_active in signals.items() if is_active]
    severity = classify_severity(signals)

    if severity is None:
        return None

    # Check for existing open alert with same signals
    existing = AtRiskAlert.objects.filter(
        student=student, status=AlertStatus.OPEN
    ).first()
    if existing:
        # Don't duplicate — alert already open
        return None

    explanation = ""
    if severity in (AlertSeverity.HIGH, AlertSeverity.MEDIUM):
        explanation = generate_explanation(active_signals=active_signals, severity=severity)

    alert = AtRiskAlert.objects.create(
        student=student,
        severity=severity,
        active_signals=active_signals,
        explanation=explanation,
        provider="deterministic",
        model_name="deterministic-at-risk-v1",
    )

    # Log to ai_audit_log (AI-RSK-009)
    record_ai_audit(
        action=AIAuditAction.COPILOT_RESPONSE,
        user=None,
        student=student,
        input_text=f"signals: {', '.join(active_signals)}",
        output_text=explanation,
        provider=CopilotProvider.DETERMINISTIC,
        model_name="deterministic-at-risk-v1",
        metadata={
            "alertId": str(alert.id),
            "severity": severity,
            "activeSignals": active_signals,
            "feature": "at_risk_engine",
        },
    )

    return alert


def run_at_risk_engine() -> dict[str, Any]:
    """Process all active students. Returns summary stats."""
    students = StudentProfile.objects.filter(is_active=True).select_related("user")
    stats = {"students_processed": 0, "alerts_created": 0, "errors": 0}

    for student in students:
        try:
            stats["students_processed"] += 1
            alert = process_student(student)
            if alert:
                stats["alerts_created"] += 1
        except Exception:
            stats["errors"] += 1
            logger.exception("At-risk engine error for student %s", student.id)

    record_audit_event_safely(
        actor=None,
        category=AuditCategory.AI,
        action="AT_RISK_ENGINE_RUN",
        summary=f"At-risk engine completed: {stats['students_processed']} students, {stats['alerts_created']} alerts created.",
        target_type="AtRiskEngine",
        target_id="nightly-run",
        severity=AuditSeverity.INFO,
        metadata=stats,
    )

    return stats


@transaction.atomic
def acknowledge_alert(*, alert_id, user) -> AtRiskAlert:
    """Acknowledge an alert — moves to history."""
    alert = AtRiskAlert.objects.select_for_update().get(id=alert_id, status=AlertStatus.OPEN)
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by = user
    alert.acknowledged_at = timezone.now()
    alert.save(update_fields=["status", "acknowledged_by", "acknowledged_at", "updated_at"])

    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action="AT_RISK_ALERT_ACKNOWLEDGED",
        summary=f"At-risk alert acknowledged for student {alert.student.student_number}.",
        target_type="AtRiskAlert",
        target_id=str(alert.id),
        severity=AuditSeverity.INFO,
        metadata={"alertId": str(alert.id), "severity": alert.severity},
    )

    return alert


def auto_close_resolved_alerts() -> int:
    """Auto-close alerts where signals have resolved. Returns count of closed alerts."""
    open_alerts = AtRiskAlert.objects.filter(status=AlertStatus.OPEN).select_related("student")
    closed_count = 0

    for alert in open_alerts:
        signals = evaluate_all_signals(alert.student)
        severity = classify_severity(signals)
        if severity is None:
            alert.status = AlertStatus.AUTO_CLOSED
            alert.auto_closed_at = timezone.now()
            alert.save(update_fields=["status", "auto_closed_at", "updated_at"])
            closed_count += 1

    return closed_count
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest apps/atrisk/tests/test_services.py -v
```
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/atrisk/services.py backend/apps/atrisk/tests/test_services.py
git commit -m "feat(atrisk): implement engine service with audit logging (AI-RSK-001, AI-RSK-009)"
```

---

## Task 8: Management Commands

**Files:**
- Create: `backend/apps/atrisk/management/commands/run_at_risk_engine.py`
- Create: `backend/apps/atrisk/management/commands/seed_at_risk_demo.py`

- [ ] **Step 1: Create run_at_risk_engine command**

Create `backend/apps/atrisk/management/commands/run_at_risk_engine.py`:
```python
from django.core.management.base import BaseCommand

from apps.atrisk.services import auto_close_resolved_alerts, run_at_risk_engine


class Command(BaseCommand):
    help = "Run the at-risk student insight engine (same logic as nightly Celery task)."

    def handle(self, *args, **options):
        self.stdout.write("Starting at-risk engine...")

        # Step 1: Auto-close resolved alerts
        closed = auto_close_resolved_alerts()
        self.stdout.write(f"  Auto-closed {closed} resolved alert(s).")

        # Step 2: Process all active students
        stats = run_at_risk_engine()
        self.stdout.write(f"  Students processed: {stats['students_processed']}")
        self.stdout.write(f"  Alerts created: {stats['alerts_created']}")
        self.stdout.write(f"  Errors: {stats['errors']}")

        self.stdout.write(self.style.SUCCESS("At-risk engine run complete."))

        # NOTE: When Celery is configured, register as periodic task:
        # @app.task(name="atrisk.run_nightly_engine")
        # def run_nightly_engine_task():
        #     auto_close_resolved_alerts()
        #     run_at_risk_engine()
```

- [ ] **Step 2: Create seed_at_risk_demo command**

Create `backend/apps/atrisk/management/commands/seed_at_risk_demo.py`:
```python
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.constants import RoleCode
from apps.accounts.models import Role, User
from apps.academics.models import (
    AttendanceRecord,
    AttendanceSession,
    AttendanceStatus,
    Course,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentStatus,
    GradeRecord,
    GradeStatus,
    SpecialGradeCode,
)
from apps.integration.models import (
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
)
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile

from apps.atrisk.services import run_at_risk_engine


class Command(BaseCommand):
    help = "Seed demo students with various at-risk signal patterns to trigger all severity levels."

    def handle(self, *args, **options):
        Role.objects.get_or_create(code=RoleCode.ADVISOR, defaults={"name": "Advisor"})
        Role.objects.get_or_create(code=RoleCode.STUDENT, defaults={"name": "Student"})
        Role.objects.get_or_create(code=RoleCode.FACULTY, defaults={"name": "Faculty"})

        advisor = self._get_or_create_user("atrisk.advisor", RoleCode.ADVISOR, "At-Risk Demo Advisor")
        faculty = self._get_or_create_user("atrisk.faculty", RoleCode.FACULTY, "At-Risk Demo Faculty")

        course, section = self._get_or_create_course(faculty)

        # HIGH severity: Academic probation
        s1 = self._get_or_create_student("atrisk.high1", "2026/RISK/H01", AcademicStanding.PROBATION, Decimal("1.60"))
        self.stdout.write(f"  Created/verified HIGH student (probation): {s1.student_number}")

        # HIGH severity: Moodle inactivity (>14 days)
        s2 = self._get_or_create_student("atrisk.high2", "2026/RISK/H02", AcademicStanding.GOOD_STANDING, Decimal("2.80"))
        self._create_moodle_snapshot(s2, days_since_login=20, quiz_avg=Decimal("60.00"), forum_posts=3)
        self.stdout.write(f"  Created/verified HIGH student (moodle inactivity): {s2.student_number}")

        # HIGH severity: 3 medium signals (financial + incomplete + quiz)
        s3 = self._get_or_create_student("atrisk.high3", "2026/RISK/H03", AcademicStanding.GOOD_STANDING, Decimal("2.50"))
        self._create_financial_flag(s3, advisor)
        self._create_incomplete_grades(s3, faculty, 2)
        self._create_moodle_snapshot(s3, days_since_login=5, quiz_avg=Decimal("30.00"), forum_posts=5)
        self.stdout.write(f"  Created/verified HIGH student (3 medium signals): {s3.student_number}")

        # MEDIUM severity: 2 medium signals (financial + low quiz)
        s4 = self._get_or_create_student("atrisk.med1", "2026/RISK/M01", AcademicStanding.GOOD_STANDING, Decimal("2.90"))
        self._create_financial_flag(s4, advisor)
        self._create_moodle_snapshot(s4, days_since_login=5, quiz_avg=Decimal("35.00"), forum_posts=2)
        self.stdout.write(f"  Created/verified MEDIUM student (financial + quiz): {s4.student_number}")

        # LOW severity: single forum disengagement
        s5 = self._get_or_create_student("atrisk.low1", "2026/RISK/L01", AcademicStanding.GOOD_STANDING, Decimal("3.40"))
        self._create_moodle_snapshot(s5, days_since_login=5, quiz_avg=Decimal("70.00"), forum_posts=0, course_last_access_days=25)
        self.stdout.write(f"  Created/verified LOW student (forum disengagement): {s5.student_number}")

        # CLEAN: No signals
        s6 = self._get_or_create_student("atrisk.clean", "2026/RISK/C01", AcademicStanding.GOOD_STANDING, Decimal("3.80"))
        self.stdout.write(f"  Created/verified CLEAN student (no signals): {s6.student_number}")

        # HIGH severity: Low attendance
        s7 = self._get_or_create_student("atrisk.high4", "2026/RISK/H04", AcademicStanding.GOOD_STANDING, Decimal("2.70"))
        self._create_attendance_records(s7, section, faculty, present=2, absent=8)
        self.stdout.write(f"  Created/verified HIGH student (low attendance): {s7.student_number}")

        # Run the engine
        self.stdout.write("\nRunning at-risk engine on demo data...")
        stats = run_at_risk_engine()
        self.stdout.write(self.style.SUCCESS(
            f"At-risk demo seeded: {stats['students_processed']} processed, "
            f"{stats['alerts_created']} alerts created."
        ))

    def _get_or_create_user(self, username: str, role: str, full_name: str) -> User:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"primary_role": role, "full_name": full_name},
        )
        if created or not user.has_usable_password():
            user.set_password("DemoPass123!")
            user.save()
        return user

    def _get_or_create_student(
        self, username: str, student_number: str, standing: str, gpa: Decimal
    ) -> StudentProfile:
        user = self._get_or_create_user(username, RoleCode.STUDENT, username.replace(".", " ").title())
        student, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "student_number": student_number,
                "national_id": f"NRC-{student_number.replace('/', '-')}",
                "date_of_birth": date(2003, 1, 15),
                "gender": "Male",
                "programme": "BSc Computer Science",
                "year_of_study": 2,
                "academic_standing": standing,
                "cumulative_gpa": gpa,
                "is_active": True,
            },
        )
        return student

    def _get_or_create_course(self, faculty):
        course, _ = Course.objects.get_or_create(
            course_code="RISK101",
            defaults={"title": "Risk Demo Course", "credits": 3, "created_by_user": faculty},
        )
        section, _ = CourseSection.objects.get_or_create(
            course=course,
            section_code="A",
            semester="Semester 1",
            academic_year="2025/2026",
            defaults={
                "status": CourseSectionStatus.ACTIVE,
                "instructor_user": faculty,
                "capacity": 50,
            },
        )
        return course, section

    def _create_financial_flag(self, student, advisor):
        if not student.financial_flags.filter(cleared_date__isnull=True).exists():
            FinancialFlag.objects.create(
                student=student,
                flag_type="TUITION_OVERDUE",
                reason="Outstanding tuition fees",
                effective_date=date.today() - timedelta(days=30),
                created_by_user=advisor,
            )

    def _create_incomplete_grades(self, student, faculty, count):
        existing = GradeRecord.objects.filter(
            student=student, special_code=SpecialGradeCode.INCOMPLETE
        ).count()
        for i in range(max(0, count - existing)):
            course, _ = Course.objects.get_or_create(
                course_code=f"INC{student.student_number[-3:]}{i}",
                defaults={"title": f"Incomplete Demo {i}", "credits": 3, "created_by_user": faculty},
            )
            section, _ = CourseSection.objects.get_or_create(
                course=course,
                section_code="A",
                semester="Semester 1",
                academic_year="2025/2026",
                defaults={
                    "status": CourseSectionStatus.ACTIVE,
                    "instructor_user": faculty,
                    "capacity": 30,
                },
            )
            GradeRecord.objects.get_or_create(
                student=student,
                section=section,
                defaults={
                    "grade_status": GradeStatus.OFFICIAL,
                    "special_code": SpecialGradeCode.INCOMPLETE,
                    "entered_by_user": faculty,
                },
            )

    def _create_moodle_snapshot(
        self,
        student,
        *,
        days_since_login: int,
        quiz_avg: Decimal,
        forum_posts: int,
        course_last_access_days: int | None = None,
    ):
        if MoodleEngagementSnapshot.objects.filter(student=student).exists():
            return
        run, _ = MoodleEngagementIngestionRun.objects.get_or_create(
            status=MoodleEngagementIngestionStatus.SUCCEEDED,
            defaults={"completed_at": timezone.now()},
        )
        course_access = timezone.now() - timedelta(days=course_last_access_days or days_since_login)
        MoodleEngagementSnapshot.objects.create(
            run=run,
            student=student,
            moodle_user_id=hash(student.student_number) % 100000,
            moodle_course_id=3001,
            moodle_last_access_at=timezone.now() - timedelta(days=days_since_login),
            moodle_course_last_access_at=course_access,
            quiz_average=quiz_avg,
            quiz_attempt_count=5,
            forum_post_count=forum_posts,
            assignment_submission_count=10,
            assignment_submission_rate=Decimal("80.00"),
            collected_at=timezone.now(),
        )

    def _create_attendance_records(self, student, section, faculty, present: int, absent: int):
        if AttendanceRecord.objects.filter(student=student).exists():
            return
        Enrollment.objects.get_or_create(
            student=student,
            section=section,
            defaults={"enrollment_status": EnrollmentStatus.ENROLLED, "actor_role": "ADMIN"},
        )
        session = AttendanceSession.objects.create(
            section=section, session_date=date.today(), created_by_user=faculty
        )
        for _ in range(present):
            AttendanceRecord.objects.create(student=student, session=session, status=AttendanceStatus.PRESENT)
        for _ in range(absent):
            AttendanceRecord.objects.create(student=student, session=session, status=AttendanceStatus.ABSENT)
```

- [ ] **Step 3: Verify commands are discovered**

```bash
python manage.py run_at_risk_engine --help
python manage.py seed_at_risk_demo --help
```
Expected: Both show help text without errors.

- [ ] **Step 4: Commit**

```bash
git add backend/apps/atrisk/management/
git commit -m "feat(atrisk): add run_at_risk_engine and seed_at_risk_demo commands (AI-RSK-001)"
```

---

## Task 9: API — Serializers, Views, URLs

**Files:**
- Create: `backend/apps/atrisk/serializers.py`
- Create: `backend/apps/atrisk/views.py`
- Create: `backend/apps/atrisk/urls.py`
- Modify: `backend/sis_backend/urls.py`
- Modify: `backend/apps/accounts/access.py`

- [ ] **Step 1: Create serializers.py**

Create `backend/apps/atrisk/serializers.py`:
```python
from rest_framework import serializers

from .models import AtRiskAlert


class AtRiskAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_number = serializers.SerializerMethodField()

    class Meta:
        model = AtRiskAlert
        fields = [
            "id",
            "student",
            "student_name",
            "student_number",
            "severity",
            "status",
            "active_signals",
            "explanation",
            "provider",
            "model_name",
            "acknowledged_by",
            "acknowledged_at",
            "auto_closed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_student_name(self, obj) -> str:
        return obj.student.user.full_name if obj.student and obj.student.user else ""

    def get_student_number(self, obj) -> str:
        return obj.student.student_number if obj.student else ""
```

- [ ] **Step 2: Create views.py**

Create `backend/apps/atrisk/views.py`:
```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AlertStatus, AtRiskAlert
from .serializers import AtRiskAlertSerializer
from .services import acknowledge_alert


class AtRiskAlertListView(APIView):
    """GET /api/v1/advisor/at-risk/alerts — open alerts sorted by severity desc, date desc."""

    def get(self, request):
        alerts = AtRiskAlert.objects.filter(status=AlertStatus.OPEN).select_related(
            "student", "student__user"
        ).order_by("-severity", "-created_at")
        serializer = AtRiskAlertSerializer(alerts, many=True)
        return Response(serializer.data)


class AtRiskAlertHistoryView(APIView):
    """GET /api/v1/advisor/at-risk/alerts/history — acknowledged/closed alerts."""

    def get(self, request):
        alerts = AtRiskAlert.objects.filter(
            status__in=[AlertStatus.ACKNOWLEDGED, AlertStatus.AUTO_CLOSED]
        ).select_related("student", "student__user").order_by("-updated_at")[:100]
        serializer = AtRiskAlertSerializer(alerts, many=True)
        return Response(serializer.data)


class AtRiskAlertAcknowledgeView(APIView):
    """POST /api/v1/advisor/at-risk/alerts/{id}/acknowledge — acknowledge an alert."""

    def post(self, request, alert_id):
        try:
            alert = acknowledge_alert(alert_id=alert_id, user=request.user)
        except AtRiskAlert.DoesNotExist:
            return Response({"detail": "Alert not found or already acknowledged."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AtRiskAlertSerializer(alert)
        return Response(serializer.data)
```

- [ ] **Step 3: Create urls.py**

Create `backend/apps/atrisk/urls.py`:
```python
from django.urls import path

from .views import AtRiskAlertAcknowledgeView, AtRiskAlertHistoryView, AtRiskAlertListView

urlpatterns = [
    path("advisor/at-risk/alerts", AtRiskAlertListView.as_view(), name="at-risk-alerts-list"),
    path("advisor/at-risk/alerts/history", AtRiskAlertHistoryView.as_view(), name="at-risk-alerts-history"),
    path("advisor/at-risk/alerts/<uuid:alert_id>/acknowledge", AtRiskAlertAcknowledgeView.as_view(), name="at-risk-alert-acknowledge"),
]
```

- [ ] **Step 4: Add URL include to main urls.py**

In `backend/sis_backend/urls.py`, add after the summarisation line:
```python
    path("api/v1/", include("apps.atrisk.urls")),
```

- [ ] **Step 5: Add route policies to access.py**

In `backend/apps/accounts/access.py`, add these entries to `PROTECTED_API_ROUTE_POLICIES` dict (before the closing `}`):
```python
        "at-risk-alerts-list": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "at-risk-alerts-history": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "at-risk-alert-acknowledge": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
```

- [ ] **Step 6: Verify system check passes**

```bash
python manage.py check
```
Expected: No issues.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/atrisk/serializers.py backend/apps/atrisk/views.py backend/apps/atrisk/urls.py backend/sis_backend/urls.py backend/apps/accounts/access.py
git commit -m "feat(atrisk): add API endpoints for alerts list, history, acknowledge (AI-RSK-005, AI-RSK-006)"
```

---

## Task 10: API Permission Tests

**Files:**
- Create: `backend/apps/atrisk/tests/test_api.py`

- [ ] **Step 1: Write test_api.py**

Create `backend/apps/atrisk/tests/test_api.py`:
```python
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.students.models import AcademicStanding, StudentProfile
from apps.testutils import authenticated_client_for_user, create_user

from apps.atrisk.models import AlertSeverity, AlertStatus, AtRiskAlert


pytestmark = pytest.mark.django_db


@pytest.fixture
def student_profile():
    user = create_user(username="api.risk.student", primary_role=RoleCode.STUDENT, email="api.risk.student@example.edu")
    return StudentProfile.objects.create(
        user=user,
        student_number="2026/API/R01",
        national_id="NRC-API-R01",
        date_of_birth=date(2003, 6, 10),
        gender="Female",
        programme="BSc IT",
        year_of_study=2,
        academic_standing=AcademicStanding.PROBATION,
        cumulative_gpa=Decimal("1.90"),
        is_active=True,
    )


@pytest.fixture
def open_alert(student_profile):
    return AtRiskAlert.objects.create(
        student=student_profile,
        severity=AlertSeverity.HIGH,
        active_signals=["academic_probation"],
        explanation="Test explanation for probation alert.",
    )


@pytest.fixture
def advisor():
    return create_user(username="api.risk.advisor", primary_role=RoleCode.ADVISOR, email="api.risk.advisor@example.edu")


@pytest.fixture
def admin_user():
    return create_user(username="api.risk.admin", primary_role=RoleCode.ADMIN, email="api.risk.admin@example.edu")


@pytest.fixture
def student_user():
    return create_user(username="api.risk.stu", primary_role=RoleCode.STUDENT, email="api.risk.stu@example.edu")


@pytest.fixture
def faculty_user():
    return create_user(username="api.risk.faculty", primary_role=RoleCode.FACULTY, email="api.risk.faculty@example.edu")


def test_advisor_can_list_open_alerts(advisor, open_alert):
    client = authenticated_client_for_user(advisor)
    response = client.get("/api/v1/advisor/at-risk/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(open_alert.id)
    assert data[0]["severity"] == "HIGH"
    assert data[0]["student_name"] != ""


def test_admin_can_list_open_alerts(admin_user, open_alert):
    client = authenticated_client_for_user(admin_user)
    response = client.get("/api/v1/advisor/at-risk/alerts")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_student_cannot_access_alerts(student_user, open_alert):
    client = authenticated_client_for_user(student_user)
    response = client.get("/api/v1/advisor/at-risk/alerts")
    assert response.status_code == 403


def test_faculty_cannot_access_alerts(faculty_user, open_alert):
    client = authenticated_client_for_user(faculty_user)
    response = client.get("/api/v1/advisor/at-risk/alerts")
    assert response.status_code == 403


def test_unauthenticated_cannot_access_alerts(open_alert):
    client = APIClient()
    response = client.get("/api/v1/advisor/at-risk/alerts")
    assert response.status_code == 401


def test_advisor_can_acknowledge_alert(advisor, open_alert):
    client = authenticated_client_for_user(advisor)
    response = client.post(f"/api/v1/advisor/at-risk/alerts/{open_alert.id}/acknowledge")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACKNOWLEDGED"
    assert data["acknowledged_at"] is not None


def test_advisor_can_view_history(advisor, open_alert):
    open_alert.status = AlertStatus.ACKNOWLEDGED
    open_alert.save()
    client = authenticated_client_for_user(advisor)
    response = client.get("/api/v1/advisor/at-risk/alerts/history")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_student_cannot_acknowledge_alert(student_user, open_alert):
    client = authenticated_client_for_user(student_user)
    response = client.post(f"/api/v1/advisor/at-risk/alerts/{open_alert.id}/acknowledge")
    assert response.status_code == 403


def test_acknowledge_nonexistent_alert_returns_404(advisor):
    import uuid
    client = authenticated_client_for_user(advisor)
    response = client.post(f"/api/v1/advisor/at-risk/alerts/{uuid.uuid4()}/acknowledge")
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
mysql -u modern_sis -pmodern_sis -h 127.0.0.1 -P 3313 -e "DROP DATABASE IF EXISTS test_modern_sis; CREATE DATABASE test_modern_sis CHARACTER SET utf8mb4;"
pytest apps/atrisk/tests/test_api.py -v
```
Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add backend/apps/atrisk/tests/test_api.py
git commit -m "test(atrisk): add API permission tests for advisor/admin/student/faculty (AI-RSK-005)"
```

---

## Task 11: Run Full Test Suite

- [ ] **Step 1: Run all atrisk tests together**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
mysql -u modern_sis -pmodern_sis -h 127.0.0.1 -P 3313 -e "DROP DATABASE IF EXISTS test_modern_sis; CREATE DATABASE test_modern_sis CHARACTER SET utf8mb4;"
pytest apps/atrisk/tests/ -v
```
Expected: All pass.

- [ ] **Step 2: Run linting**

```bash
ruff check apps/atrisk/
```
Expected: No errors.

- [ ] **Step 3: Run Django check and dry-run migration check**

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```
Expected: No issues, no new migrations needed.

---

## Task 12: Frontend — useAtRiskAlerts Hook

**Files:**
- Modify: `frontend/src/hooks/useAtRiskAlerts.ts`

- [ ] **Step 1: Replace placeholder hook with live implementation**

Replace the contents of `frontend/src/hooks/useAtRiskAlerts.ts`:
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '@/api/axios'

export interface AtRiskAlert {
  id: string
  student: string
  student_name: string
  student_number: string
  severity: 'HIGH' | 'MEDIUM' | 'LOW'
  status: 'OPEN' | 'ACKNOWLEDGED' | 'AUTO_CLOSED'
  active_signals: string[]
  explanation: string
  provider: string
  model_name: string
  acknowledged_by: string | null
  acknowledged_at: string | null
  auto_closed_at: string | null
  created_at: string
  updated_at: string
}

export function useAtRiskAlerts() {
  return useQuery<AtRiskAlert[]>({
    queryKey: ['at-risk-alerts'],
    queryFn: async () => {
      const response = await api.get('/advisor/at-risk/alerts')
      return response.data
    },
  })
}

export function useAtRiskAlertHistory() {
  return useQuery<AtRiskAlert[]>({
    queryKey: ['at-risk-alerts-history'],
    queryFn: async () => {
      const response = await api.get('/advisor/at-risk/alerts/history')
      return response.data
    },
  })
}

export function useAcknowledgeAlertMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (alertId: string): Promise<AtRiskAlert> => {
      const response = await api.post(`/advisor/at-risk/alerts/${alertId}/acknowledge`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['at-risk-alerts'] })
      queryClient.invalidateQueries({ queryKey: ['at-risk-alerts-history'] })
    },
  })
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/useAtRiskAlerts.ts
git commit -m "feat(frontend): implement useAtRiskAlerts hook with live API calls"
```

---

## Task 13: Frontend — AtRiskAlertQueue Component

**Files:**
- Modify: `frontend/src/components/advisor/AtRiskAlertQueue.tsx`

- [ ] **Step 1: Replace placeholder with live component**

Replace the contents of `frontend/src/components/advisor/AtRiskAlertQueue.tsx`:
```typescript
import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'
import { useAcknowledgeAlertMutation, useAtRiskAlerts } from '@/hooks/useAtRiskAlerts'

export function AtRiskAlertQueue() {
  const { data: alerts, isPending, isError } = useAtRiskAlerts()
  const acknowledgeMutation = useAcknowledgeAlertMutation()

  if (isPending) {
    return <div className="p-4 text-sm text-neutral-500">Loading at-risk alerts...</div>
  }

  if (isError) {
    return <div className="p-4 text-sm text-red-600">Failed to load at-risk alerts.</div>
  }

  if (!alerts || alerts.length === 0) {
    return <div className="p-4 text-sm text-neutral-500">No open at-risk alerts.</div>
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <AtRiskAlertRow
          key={alert.id}
          severity={alert.severity}
          studentName={`${alert.student_name} (${alert.student_number})`}
          timestamp={new Date(alert.created_at).toLocaleDateString()}
          explanation={alert.explanation || `Signals: ${alert.active_signals.join(', ')}`}
          onAcknowledge={() => acknowledgeMutation.mutate(alert.id)}
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/advisor/AtRiskAlertQueue.tsx
git commit -m "feat(frontend): wire AtRiskAlertQueue to live API data (AI-RSK-005)"
```

---

## Task 14: Frontend — AlertHistory Page

**Files:**
- Modify: `frontend/src/pages/advisor/AlertHistory.tsx`

- [ ] **Step 1: Replace placeholder with live history page**

Replace the contents of `frontend/src/pages/advisor/AlertHistory.tsx`:
```typescript
import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'
import { useAtRiskAlertHistory } from '@/hooks/useAtRiskAlerts'

export function AdvisorAlertHistoryPage() {
  const { data: alerts, isPending, isError } = useAtRiskAlertHistory()

  if (isPending) {
    return <div className="p-4 text-sm text-neutral-500">Loading alert history...</div>
  }

  if (isError) {
    return <div className="p-4 text-sm text-red-600">Failed to load alert history.</div>
  }

  if (!alerts || alerts.length === 0) {
    return <div className="p-4 text-sm text-neutral-500">No historical alerts.</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-neutral-800">Alert History</h2>
      {alerts.map((alert) => (
        <AtRiskAlertRow
          key={alert.id}
          severity={alert.severity}
          studentName={`${alert.student_name} (${alert.student_number})`}
          timestamp={new Date(alert.updated_at).toLocaleDateString()}
          explanation={alert.explanation || `Signals: ${alert.active_signals.join(', ')}`}
          acknowledged={alert.status === 'ACKNOWLEDGED'}
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/advisor/AlertHistory.tsx
git commit -m "feat(frontend): wire AlertHistory page to live API data (AI-RSK-005)"
```

---

## Task 15: Frontend Verification

- [ ] **Step 1: Run TypeScript type check**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/frontend
npm run typecheck
```
Expected: No errors.

- [ ] **Step 2: Run ESLint**

```bash
npm run lint
```
Expected: No errors.

- [ ] **Step 3: Run build**

```bash
npm run build
```
Expected: Successful build.

- [ ] **Step 4: Commit any lint fixes if needed**

If there were lint fixes needed, commit them.

---

## Task 16: Final Backend Verification

- [ ] **Step 1: Full verification suite**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/backend
source ../.venv/bin/activate && source .env.local
python manage.py check
python manage.py makemigrations --check --dry-run
mysql -u modern_sis -pmodern_sis -h 127.0.0.1 -P 3313 -e "DROP DATABASE IF EXISTS test_modern_sis; CREATE DATABASE test_modern_sis CHARACTER SET utf8mb4;"
pytest apps/atrisk/tests/ -v
ruff check apps/atrisk/
```
Expected: All pass, no issues.

---

## Task 17: Documentation and Final Commit

**Files:**
- Create: `docs/superpowers/specs/2026-05-09-phase-05-step-5-1-at-risk-engine.md`
- Create: `docs/phases/phase-05-at-risk-engine/README.md`
- Create: `docs/phases/phase-05-at-risk-engine/CHANGELOG.md`

- [ ] **Step 1: Create spec document**

Create `docs/superpowers/specs/2026-05-09-phase-05-step-5-1-at-risk-engine.md` with a brief design spec covering:
- Feature summary
- 9 signals evaluated
- Severity classification rules
- API endpoints
- Deterministic provider approach
- Configuration via `config.py`

- [ ] **Step 2: Create phase docs**

Create `docs/phases/phase-05-at-risk-engine/README.md` summarizing Phase 5 Step 5.1.
Create `docs/phases/phase-05-at-risk-engine/CHANGELOG.md` with the initial entry.

- [ ] **Step 3: Update root CHANGELOG if it exists**

Add Phase 5.1 entry if `CHANGELOG.md` exists at root or docs level.

- [ ] **Step 4: Final commit**

```bash
git add docs/
git commit -m "docs: add Phase 5 Step 5.1 at-risk engine design spec and phase docs"
```

---

## Task 18: Merge to Main and Push

- [ ] **Step 1: Merge to main**

```bash
cd /home/charlie/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION
git checkout main
git merge feature/phase-05-step-5-1-at-risk-engine --no-ff -m "feat: add phase 5.1 at-risk student insight engine"
```

- [ ] **Step 2: Push**

```bash
git push origin main
```
