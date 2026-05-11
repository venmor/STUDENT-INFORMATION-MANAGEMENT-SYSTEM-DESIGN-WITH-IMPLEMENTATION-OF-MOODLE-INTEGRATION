from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from apps.accounts.constants import RoleCode
from apps.students.models import AcademicStanding, StudentProfile
from apps.testutils import create_user

from apps.atrisk.models import AlertSeverity, AtRiskAlert
from apps.atrisk.services import (
    acknowledge_alert,
    auto_close_resolved_alerts,
    process_student,
    run_at_risk_engine,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def advisor():
    return create_user(username="svc.t.advisor", primary_role=RoleCode.ADVISOR, email="svc.t.advisor@example.edu")


@pytest.fixture
def student_on_probation():
    user = create_user(username="svc.t.probation", primary_role=RoleCode.STUDENT, email="svc.t.probation@example.edu")
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
    user = create_user(username="svc.t.clean", primary_role=RoleCode.STUDENT, email="svc.t.clean@example.edu")
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
    assert alert.is_acknowledged is False
    assert alert.is_closed is False
    assert "academic_probation" in alert.active_signals
    assert alert.explanation != ""


def test_process_student_returns_none_for_clean_student(clean_student):
    alert = process_student(clean_student)
    assert alert is None


def test_process_student_updates_existing_alert(student_on_probation):
    alert1 = process_student(student_on_probation)
    assert alert1 is not None
    alert2 = process_student(student_on_probation)
    # Should update existing, not create new
    assert alert2 is not None
    assert alert2.id == alert1.id
    assert AtRiskAlert.objects.filter(
        student=student_on_probation, is_closed=False, is_acknowledged=False
    ).count() == 1


def test_run_at_risk_engine_processes_all_active_students(student_on_probation, clean_student):
    stats = run_at_risk_engine()
    assert stats["students_processed"] == 2
    assert stats["alerts_created"] == 1


def test_acknowledge_alert(student_on_probation, advisor):
    alert = process_student(student_on_probation)
    assert alert is not None
    acknowledged = acknowledge_alert(alert_id=alert.id, user=advisor)
    assert acknowledged.is_acknowledged is True
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
    assert alert.is_closed is True
    assert alert.closed_at is not None


def test_process_student_closes_open_alert_when_resolved(student_on_probation):
    alert = process_student(student_on_probation)
    assert alert is not None
    # Fix the student
    student_on_probation.academic_standing = AcademicStanding.GOOD_STANDING
    student_on_probation.save()
    result = process_student(student_on_probation)
    assert result is None
    alert.refresh_from_db()
    assert alert.is_closed is True
