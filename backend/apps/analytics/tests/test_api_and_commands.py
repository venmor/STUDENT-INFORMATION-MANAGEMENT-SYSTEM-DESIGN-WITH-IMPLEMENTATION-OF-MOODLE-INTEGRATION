from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.analytics.models import AnalyticsETLRun, StudentAnalyticsSnapshot
from apps.testutils import authenticated_client_for_user, create_user


pytestmark = pytest.mark.django_db


def test_seed_analytics_demo_and_run_command_create_repeatable_snapshots():
    seed_stdout = StringIO()
    call_command("seed_analytics_demo", stdout=seed_stdout)
    call_command("seed_analytics_demo", stdout=StringIO())

    etl_stdout = StringIO()
    call_command("run_analytics_etl", "--academic-year", "2026/2027", "--semester", "Semester 1", stdout=etl_stdout)

    assert "Analytics demo data is ready" in seed_stdout.getvalue()
    output = etl_stdout.getvalue()
    assert "Analytics ETL complete" in output
    assert "status: SUCCEEDED" in output
    assert AnalyticsETLRun.objects.count() == 1
    assert StudentAnalyticsSnapshot.objects.count() >= 2


def test_admin_can_view_analytics_summary_and_snapshots_but_non_admins_cannot():
    call_command("seed_analytics_demo", stdout=StringIO())
    call_command("run_analytics_etl", "--academic-year", "2026/2027", "--semester", "Semester 1", stdout=StringIO())
    admin = create_user(username="analytics-api-admin", primary_role=RoleCode.ADMIN, email="analytics-api-admin@example.com")
    student = create_user(username="analytics-api-student", primary_role=RoleCode.STUDENT, email="analytics-api-student@example.com")

    admin_client = authenticated_client_for_user(admin)
    summary_response = admin_client.get("/api/v1/admin/analytics/summary/")
    snapshots_response = admin_client.get("/api/v1/admin/analytics/snapshots/?limit=5")
    runs_response = admin_client.get("/api/v1/admin/analytics/etl-runs/")
    detail_id = snapshots_response.json()[0]["id"]
    detail_response = admin_client.get(f"/api/v1/admin/analytics/snapshots/{detail_id}/")

    assert summary_response.status_code == 200
    assert summary_response.json()["studentsWithSnapshots"] >= 2
    assert snapshots_response.status_code == 200
    assert "student" in snapshots_response.json()[0]
    assert runs_response.status_code == 200
    assert detail_response.status_code == 200

    student_client = authenticated_client_for_user(student)
    assert student_client.get("/api/v1/admin/analytics/summary/").status_code == 403
    assert APIClient().get("/api/v1/admin/analytics/summary/").status_code == 401
