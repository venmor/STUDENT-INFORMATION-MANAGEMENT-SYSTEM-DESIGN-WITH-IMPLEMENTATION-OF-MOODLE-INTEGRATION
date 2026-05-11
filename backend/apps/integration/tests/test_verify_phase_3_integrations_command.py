from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import Mock

from django.core.management import call_command
from django.utils import timezone

from apps.academics.models import Course, CourseSection, CourseSectionStatus
from apps.accounts.constants import RoleCode
from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleUserMap,
)
from apps.testutils import create_user


def create_mapped_course():
    faculty = create_user(
        username="readiness-faculty",
        email="readiness-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Readiness Faculty",
    )
    course = Course.objects.create(
        course_code="CSC490",
        course_title="Integration Readiness",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=50,
        is_active=True,
    )
    now = timezone.now()
    section = CourseSection.objects.create(
        course=course,
        section_code="A1",
        faculty_user=faculty,
        room="LT-10",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=50,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=14),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    return MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=9910,
        moodle_shortname="CSC490-A1-2026_2027-SEM1",
        moodle_category_id=7,
    )


def test_verify_phase_3_integrations_reports_local_readiness_without_live_moodle(
    settings, monkeypatch, db
):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.LTI_CLIENT_ID = "client-123"
    settings.LTI_DEPLOYMENT_ID = "deployment-456"
    settings.LTI_PLATFORM_ISSUER_ALLOWLIST = ["https://moodle.example.test"]
    settings.LTI_PRIVATE_KEY = "local-private-key-placeholder"
    settings.LTI_PUBLIC_KEY = "local-public-key-placeholder"
    monkeypatch.setattr(
        "requests.post",
        Mock(side_effect=AssertionError("live Moodle should not be called")),
    )
    monkeypatch.setattr(
        "requests.get",
        Mock(side_effect=AssertionError("live Moodle should not be called")),
    )

    user = create_user(
        username="readiness-user",
        email="readiness-user@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Readiness Student",
    )
    MoodleUserMap.objects.create(
        user=user, moodle_user_id=7701, moodle_username=user.username
    )
    create_mapped_course()
    IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED", payload={"user_id": user.id}
    )
    IntegrationOutboxEvent.objects.create(
        event_type="COURSE_SYNC_REQUESTED",
        payload={"section_id": "missing"},
        status=IntegrationEventStatus.FAILED,
        last_error="previous safe error",
    )
    MoodleEngagementIngestionRun.objects.create(
        status=MoodleEngagementIngestionStatus.SUCCEEDED,
        courses_inspected=1,
        users_inspected=1,
        snapshots_created=1,
        completed_at=timezone.now(),
    )
    stdout = StringIO()

    call_command("verify_phase_3_integrations", stdout=stdout)

    output = stdout.getvalue()
    assert "Phase 3 integration readiness" in output
    assert "Moodle REST config: present" in output
    assert "LTI config: present" in output
    assert "Moodle user mappings: 1" in output
    assert "Moodle course mappings: 1" in output
    assert "Pending outbox events: 1" in output
    assert "Failed outbox events: 1" in output
    assert "Latest engagement ingestion: SUCCEEDED" in output
    assert "super-secret-token" not in output
