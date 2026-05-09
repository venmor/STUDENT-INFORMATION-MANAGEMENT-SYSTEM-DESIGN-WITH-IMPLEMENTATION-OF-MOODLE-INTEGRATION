from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.students.models import AcademicStanding, StudentProfile
from apps.testutils import authenticated_client_for_user, create_user

from apps.atrisk.models import AlertSeverity, AtRiskAlert


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
        provider="deterministic",
        model_name="deterministic-at-risk-v1",
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
    assert data["is_acknowledged"] is True
    assert data["acknowledged_at"] is not None


def test_advisor_can_view_history(advisor, open_alert):
    open_alert.is_acknowledged = True
    open_alert.save()
    client = authenticated_client_for_user(advisor)
    response = client.get("/api/v1/advisor/at-risk/history")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_student_cannot_acknowledge_alert(student_user, open_alert):
    client = authenticated_client_for_user(student_user)
    response = client.post(f"/api/v1/advisor/at-risk/alerts/{open_alert.id}/acknowledge")
    assert response.status_code == 403


def test_acknowledge_nonexistent_alert_returns_404(advisor):
    client = authenticated_client_for_user(advisor)
    response = client.post(f"/api/v1/advisor/at-risk/alerts/{uuid.uuid4()}/acknowledge")
    assert response.status_code == 404
