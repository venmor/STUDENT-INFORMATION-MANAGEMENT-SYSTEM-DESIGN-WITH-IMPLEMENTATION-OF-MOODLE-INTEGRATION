from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import Mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

import pytest

from apps.academics.models import Course, CourseSection, CourseSectionStatus
from apps.accounts.constants import RoleCode
from apps.integration.models import (
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.students.models import StudentProfile
from apps.testutils import create_user


def configure_moodle_settings(settings):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.MOODLE_SYNC_TIMEOUT = 10


def build_response(payload):
    response = Mock()
    response.raise_for_status.side_effect = None
    response.json.return_value = payload
    return response


def create_mapped_student_and_section():
    student_user = create_user(
        username="command-engagement-student",
        email="command-engagement-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Command Engagement Student",
    )
    student = StudentProfile.objects.create(
        user=student_user,
        student_number="2026/CS/120",
        national_id="NRC-2026/CS/120",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=3,
    )
    faculty = create_user(
        username="command-engagement-faculty",
        email="command-engagement-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Command Engagement Faculty",
    )
    course = Course.objects.create(
        course_code="CSC480",
        course_title="Integration Analytics",
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
        room="LT-9",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=50,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=14),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    MoodleUserMap.objects.create(
        user=student_user, moodle_user_id=6601, moodle_username=student_user.username
    )
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=9901,
        moodle_shortname="CSC480-A1-2026_2027-SEM1",
        moodle_category_id=7,
    )
    return student, section


def test_ingest_moodle_engagement_command_creates_snapshots(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    create_mapped_student_and_section()
    stdout = StringIO()
    monkeypatch.setattr(
        "requests.post",
        Mock(
            return_value=build_response(
                [
                    {
                        "id": 6601,
                        "lastaccess": 1_775_000_000,
                        "lastcourseaccess": 1_775_100_000,
                    }
                ]
            )
        ),
    )

    call_command("ingest_moodle_engagement", stdout=stdout)

    run = MoodleEngagementIngestionRun.objects.get()
    assert run.status == MoodleEngagementIngestionStatus.SUCCEEDED
    assert run.snapshots_created == 1
    assert MoodleEngagementSnapshot.objects.count() == 1
    output = stdout.getvalue()
    assert "Moodle engagement ingestion complete" in output
    assert "courses_inspected=1" in output
    assert "users_inspected=1" in output
    assert "snapshots_created=1" in output
    assert "super-secret-token" not in output


def test_ingest_moodle_engagement_command_dry_run_creates_no_snapshots(
    settings, monkeypatch, db
):
    configure_moodle_settings(settings)
    create_mapped_student_and_section()
    stdout = StringIO()
    monkeypatch.setattr(
        "requests.post",
        Mock(return_value=build_response([{"id": 6601, "lastaccess": 1_775_000_000}])),
    )

    call_command("ingest_moodle_engagement", "--dry-run", stdout=stdout)

    run = MoodleEngagementIngestionRun.objects.get()
    assert run.status == MoodleEngagementIngestionStatus.DRY_RUN
    assert run.dry_run is True
    assert run.users_inspected == 1
    assert MoodleEngagementSnapshot.objects.count() == 0
    output = stdout.getvalue()
    assert "dry_run=True" in output
    assert "snapshots_created=0" in output


def test_ingest_moodle_engagement_command_requires_config(settings, db):
    settings.MOODLE_BASE_URL = ""
    settings.MOODLE_WS_TOKEN = "super-secret-token"

    with pytest.raises(CommandError, match="MOODLE_BASE_URL"):
        call_command("ingest_moodle_engagement")
