from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from json import JSONDecodeError
from unittest.mock import Mock

import pytest
import requests
from django.utils import timezone

from apps.academics.models import Course, CourseSection, CourseSectionStatus
from apps.accounts.constants import RoleCode
from apps.integration.models import (
    MoodleCourseMap,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.integration.services import MoodleEngagementError, MoodleEngagementService
from apps.students.models import StudentProfile
from apps.testutils import create_user


def build_response(*, payload=None, status_code=200, json_error=None):
    response = Mock()
    response.status_code = status_code
    response.raise_for_status.side_effect = None
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"{status_code} error"
        )
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = payload
    return response


def configure_moodle_settings(settings):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.MOODLE_SYNC_TIMEOUT = 10


def create_student_profile(
    *, username: str = "engagement-student", student_number: str = "2026/CS/090"
):
    user = create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Engagement Student",
    )
    student = StudentProfile.objects.create(
        user=user,
        student_number=student_number,
        national_id=f"NRC-{student_number}",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=3,
    )
    return user, student


def create_mapped_section(*, course_code: str = "CSC470"):
    faculty = create_user(
        username=f"faculty-{course_code.lower()}",
        email=f"faculty-{course_code.lower()}@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Engagement Faculty",
    )
    course = Course.objects.create(
        course_code=course_code,
        course_title=f"{course_code} Title",
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
        room="LT-8",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=50,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=14),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    course_map = MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=8801,
        moodle_shortname=f"{course_code}-A1-2026_2027-SEM1",
        moodle_category_id=7,
    )
    return section, course_map


def create_mapped_user():
    user, student = create_student_profile()
    user_map = MoodleUserMap.objects.create(
        user=user,
        moodle_user_id=5501,
        moodle_username=user.username,
    )
    return user, student, user_map


def test_engagement_ingestion_creates_snapshot_for_mapped_user_and_course(
    settings, monkeypatch, db
):
    configure_moodle_settings(settings)
    user, student, _ = create_mapped_user()
    section, _ = create_mapped_section()
    post_mock = Mock(
        return_value=build_response(
            payload=[
                {
                    "id": 5501,
                    "username": user.username,
                    "lastaccess": 1_775_000_000,
                    "lastcourseaccess": 1_775_100_000,
                    "roles": [{"shortname": "student"}],
                }
            ]
        )
    )
    monkeypatch.setattr("requests.post", post_mock)

    run = MoodleEngagementService().ingest()

    assert run.status == MoodleEngagementIngestionStatus.SUCCEEDED
    assert run.courses_inspected == 1
    assert run.users_inspected == 1
    assert run.snapshots_created == 1
    snapshot = MoodleEngagementSnapshot.objects.get()
    assert snapshot.run == run
    assert snapshot.user == user
    assert snapshot.student == student
    assert snapshot.section == section
    assert snapshot.moodle_user_id == 5501
    assert snapshot.moodle_course_id == 8801
    assert snapshot.moodle_last_access_at is not None
    assert snapshot.moodle_course_last_access_at is not None
    assert snapshot.assignment_submission_count is None
    assert snapshot.quiz_average is None
    assert snapshot.forum_post_count is None
    assert snapshot.raw_summary["source"] == "core_enrol_get_enrolled_users"
    payload = post_mock.call_args.kwargs["data"]
    assert payload["wsfunction"] == "core_enrol_get_enrolled_users"
    assert payload["courseid"] == 8801
    assert payload["wstoken"] == "super-secret-token"


def test_engagement_ingestion_requires_moodle_config(settings, db):
    settings.MOODLE_BASE_URL = ""
    settings.MOODLE_WS_TOKEN = "super-secret-token"

    with pytest.raises(MoodleEngagementError, match="MOODLE_BASE_URL"):
        MoodleEngagementService().ingest()


def test_engagement_ingestion_records_http_failure_without_token_leakage(
    settings, monkeypatch, db
):
    configure_moodle_settings(settings)
    create_mapped_section()
    monkeypatch.setattr(
        "requests.post", Mock(return_value=build_response(status_code=500))
    )

    run = MoodleEngagementService().ingest()

    assert run.status == MoodleEngagementIngestionStatus.FAILED
    assert run.failure_count == 1
    assert "core_enrol_get_enrolled_users" in run.last_error
    assert "super-secret-token" not in run.last_error


def test_engagement_ingestion_records_moodle_exception_without_token_leakage(
    settings, monkeypatch, db
):
    configure_moodle_settings(settings)
    create_mapped_section()
    monkeypatch.setattr(
        "requests.post",
        Mock(
            return_value=build_response(
                payload={
                    "exception": "webservice_access_exception",
                    "errorcode": "accessexception",
                    "message": "Access control exception",
                }
            )
        ),
    )

    run = MoodleEngagementService().ingest()

    assert run.status == MoodleEngagementIngestionStatus.FAILED
    assert "webservice_access_exception" in run.last_error
    assert "super-secret-token" not in run.last_error


def test_engagement_ingestion_records_invalid_json_without_token_leakage(
    settings, monkeypatch, db
):
    configure_moodle_settings(settings)
    create_mapped_section()
    monkeypatch.setattr(
        "requests.post",
        Mock(
            return_value=build_response(
                json_error=JSONDecodeError("Expecting value", "not-json", 0)
            )
        ),
    )

    run = MoodleEngagementService().ingest()

    assert run.status == MoodleEngagementIngestionStatus.FAILED
    assert "invalid JSON" in run.last_error
    assert "super-secret-token" not in run.last_error


def test_engagement_ingestion_skips_unmapped_moodle_users(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    create_mapped_section()
    monkeypatch.setattr(
        "requests.post",
        Mock(
            return_value=build_response(
                payload=[{"id": 9999, "lastaccess": 1_775_000_000}]
            )
        ),
    )

    run = MoodleEngagementService().ingest()

    assert run.status == MoodleEngagementIngestionStatus.SUCCEEDED
    assert run.users_inspected == 1
    assert run.skipped_unmapped_users == 1
    assert MoodleEngagementSnapshot.objects.count() == 0


def test_engagement_ingestion_since_filter_skips_old_access(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    create_mapped_user()
    create_mapped_section()
    old_access = int((timezone.now() - timedelta(days=30)).timestamp())
    since = timezone.now() - timedelta(days=7)
    monkeypatch.setattr(
        "requests.post",
        Mock(
            return_value=build_response(
                payload=[{"id": 5501, "lastaccess": old_access}]
            )
        ),
    )

    run = MoodleEngagementService().ingest(since=since)

    assert run.status == MoodleEngagementIngestionStatus.SUCCEEDED
    assert run.users_inspected == 1
    assert run.snapshots_created == 0
    assert MoodleEngagementSnapshot.objects.count() == 0
