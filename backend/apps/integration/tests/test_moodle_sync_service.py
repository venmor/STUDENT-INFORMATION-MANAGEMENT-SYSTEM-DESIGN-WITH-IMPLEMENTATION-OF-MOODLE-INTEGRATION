from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from json import JSONDecodeError
from unittest.mock import Mock

import pytest
import requests
from django.utils import timezone

from apps.accounts.constants import RoleCode
from apps.academics.models import Course, CourseSection, CourseSectionStatus
from apps.academics.services import create_enrollment, officialise_grade, record_grade
from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleUserMap,
)
from apps.integration.services import MoodleSyncError, MoodleSyncService, process_outbox_event
from apps.students.models import StudentProfile
from apps.testutils import create_user


def build_response(*, payload=None, status_code=200, json_error=None):
    response = Mock()
    response.status_code = status_code
    response.raise_for_status.side_effect = None
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(f"{status_code} error")
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = payload
    return response


def create_student_profile(*, username: str, student_number: str, full_name: str = "Test Student"):
    user = create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name=full_name,
    )
    profile = StudentProfile.objects.create(
        user=user,
        student_number=student_number,
        national_id=f"NRC-{student_number}",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=3,
    )
    return user, profile


def create_section(*, faculty_username: str = "faculty-sync", course_code: str = "CSC410"):
    faculty_user = create_user(
        username=faculty_username,
        email=f"{faculty_username}@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Faculty Sync",
    )
    course = Course.objects.create(
        course_code=course_code,
        course_title=f"{course_code} Title",
        department="Computer Science",
        credit_hours=3,
        description="Provisionable course",
        programme_code="BSc Computer Science",
        max_capacity=50,
        is_active=True,
    )
    now = timezone.now()
    section = CourseSection.objects.create(
        course=course,
        section_code="A1",
        faculty_user=faculty_user,
        room="LT-4",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=50,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=14),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    return faculty_user, course, section


def create_official_grade_record():
    admin_user = create_user(
        username="admin-sync",
        email="admin-sync@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Sync",
    )
    faculty_user, _, section = create_section()
    student_user, student = create_student_profile(username="grade-sync-student", student_number="2026/CS/010")
    create_enrollment(
        student=student,
        section=section,
        actor_user=admin_user,
        actor_role=RoleCode.ADMIN,
        allow_waitlist=False,
    )
    draft_grade = record_grade(
        student=student,
        section=section,
        actor_user=faculty_user,
        numeric_score="88.00",
        special_code="",
    )
    official_grade = officialise_grade(grade_record=draft_grade, actor_user=admin_user)
    return student_user, student, section, official_grade


def configure_moodle_settings(settings):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.MOODLE_DEFAULT_CATEGORY_ID = 7
    settings.MOODLE_STUDENT_ROLE_ID = 5
    settings.MOODLE_EDITING_TEACHER_ROLE_ID = 3
    settings.MOODLE_INSTITUTION = "Student Information System"
    settings.MOODLE_GRADE_SOURCE = "modern_sis"


def test_sync_user_creates_moodle_user_and_mapping(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    user = create_user(
        username="moodle-student",
        email="moodle-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Moodle Student",
    )
    post_mock = Mock(
        side_effect=[
            build_response(payload=[{"id": 55, "username": "moodle-student"}]),
            build_response(payload={"users": [{"id": 55, "username": "moodle-student"}]}),
        ]
    )
    monkeypatch.setattr("requests.post", post_mock)

    mapping = MoodleSyncService().sync_user(user)

    assert mapping.moodle_user_id == 55
    assert mapping.moodle_username == "moodle-student"
    assert MoodleUserMap.objects.get(user=user).moodle_user_id == 55
    first_call = post_mock.call_args_list[0].kwargs["data"]
    assert first_call["wsfunction"] == "core_user_create_users"
    assert first_call["users[0][username]"] == "moodle-student"
    assert first_call["users[0][institution]"] == "Student Information System"


def test_sync_user_updates_existing_mapped_user(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    user = create_user(
        username="mapped-student",
        email="mapped-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Mapped Student",
    )
    MoodleUserMap.objects.create(user=user, moodle_user_id=91, moodle_username="mapped-student")
    post_mock = Mock(return_value=build_response(payload=[]))
    monkeypatch.setattr("requests.post", post_mock)

    mapping = MoodleSyncService().sync_user(user)

    assert mapping.moodle_user_id == 91
    payload = post_mock.call_args.kwargs["data"]
    assert payload["wsfunction"] == "core_user_update_users"
    assert payload["users[0][id]"] == 91
    assert payload["users[0][email]"] == "mapped-student@example.com"


def test_sync_user_falls_back_to_lookup_when_moodle_reports_existing_username(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    user = create_user(
        username="existing-user",
        email="existing-user@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Existing User",
    )
    post_mock = Mock(
        side_effect=[
            build_response(
                payload={
                    "exception": "invalid_parameter_exception",
                    "errorcode": "invalidparameter",
                    "message": "Username already exists: existing-user",
                }
            ),
            build_response(payload={"users": [{"id": 77, "username": "existing-user"}]}),
        ]
    )
    monkeypatch.setattr("requests.post", post_mock)

    mapping = MoodleSyncService().sync_user(user)

    assert mapping.moodle_user_id == 77
    assert mapping.moodle_username == "existing-user"
    assert post_mock.call_count == 2


def test_process_outbox_event_marks_failure_without_token_leakage(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    user = create_user(
        username="broken-sync-user",
        email="broken-sync@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Broken Sync User",
    )
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": user.id, "action": "UPSERT"},
    )
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

    result = process_outbox_event(event.id)

    event.refresh_from_db()
    assert result is False
    assert event.status == IntegrationEventStatus.FAILED
    assert event.attempts == 1
    assert "webservice_access_exception" in event.last_error
    assert "super-secret-token" not in event.last_error


def test_sync_section_creates_moodle_course_mapping(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    _, _, section = create_section(course_code="CSC420")
    post_mock = Mock(return_value=build_response(payload=[{"id": 88, "shortname": "CSC420-A1-2026_2027-SEM1"}]))
    monkeypatch.setattr("requests.post", post_mock)

    mapping = MoodleSyncService().sync_section(section)

    assert mapping.moodle_course_id == 88
    assert mapping.section == section
    payload = post_mock.call_args.kwargs["data"]
    assert payload["wsfunction"] == "core_course_create_courses"
    assert payload["courses[0][categoryid]"] == 7


def test_sync_enrollment_uses_mapped_moodle_ids(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    admin_user = create_user(
        username="enrollment-admin",
        email="enrollment-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Enrollment Admin",
    )
    student_user, student = create_student_profile(username="enroll-target", student_number="2026/CS/011")
    _, _, section = create_section(course_code="CSC430")
    MoodleUserMap.objects.create(user=student_user, moodle_user_id=301, moodle_username=student_user.username)
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=401,
        moodle_shortname="CSC430-A1-2026_2027-SEM1",
        moodle_category_id=7,
    )
    enrollment = create_enrollment(
        student=student,
        section=section,
        actor_user=admin_user,
        actor_role=RoleCode.ADMIN,
        allow_waitlist=False,
    )
    post_mock = Mock(return_value=build_response(payload=[]))
    monkeypatch.setattr("requests.post", post_mock)

    MoodleSyncService().sync_enrollment(enrollment, action="ENROLL")

    payload = post_mock.call_args.kwargs["data"]
    assert payload["wsfunction"] == "enrol_manual_enrol_users"
    assert payload["enrolments[0][userid]"] == 301
    assert payload["enrolments[0][courseid]"] == 401
    assert payload["enrolments[0][roleid]"] == 5


def test_sync_official_grade_calls_grade_lookup_then_update(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    student_user, _, section, grade_record = create_official_grade_record()
    MoodleUserMap.objects.create(user=student_user, moodle_user_id=501, moodle_username=student_user.username)
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=601,
        moodle_shortname="CSC410-A1-2026_2027-SEM1",
        moodle_category_id=7,
        grade_component="mod_assign",
        grade_activity_id=71,
        grade_item_number=0,
        grade_item_label="Coursework",
    )
    post_mock = Mock(
        side_effect=[
            build_response(payload={"usergrades": [{"userid": 501, "gradeitems": []}]}),
            build_response(payload=1),
        ]
    )
    monkeypatch.setattr("requests.post", post_mock)

    MoodleSyncService().sync_grade_record(grade_record)

    first_payload = post_mock.call_args_list[0].kwargs["data"]
    second_payload = post_mock.call_args_list[1].kwargs["data"]
    assert first_payload["wsfunction"] == "gradereport_user_get_grade_items"
    assert first_payload["courseid"] == 601
    assert first_payload["userid"] == 501
    assert second_payload["wsfunction"] == "core_grades_update_grades"
    assert second_payload["courseid"] == 601
    assert second_payload["component"] == "mod_assign"
    assert second_payload["activityid"] == 71
    assert second_payload["itemnumber"] == 0
    assert second_payload["grades[0][studentid]"] == 501
    assert second_payload["grades[0][grade]"] == "88.00"


def test_sync_official_grade_requires_explicit_grade_target(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    student_user, _, section, grade_record = create_official_grade_record()
    MoodleUserMap.objects.create(user=student_user, moodle_user_id=701, moodle_username=student_user.username)
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=801,
        moodle_shortname="CSC410-A1-2026_2027-SEM1",
        moodle_category_id=7,
    )
    monkeypatch.setattr("requests.post", Mock(return_value=build_response(payload={"usergrades": [{"userid": 701}]})))

    with pytest.raises(MoodleSyncError, match="grade target"):
        MoodleSyncService().sync_grade_record(grade_record)


def test_sync_service_reports_invalid_json_without_token_leakage(settings, monkeypatch, db):
    configure_moodle_settings(settings)
    user = create_user(
        username="json-error-user",
        email="json-error-user@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Json Error User",
    )
    monkeypatch.setattr(
        "requests.post",
        Mock(
            return_value=build_response(
                json_error=JSONDecodeError("Expecting value", "not-json", 0),
            )
        ),
    )

    with pytest.raises(MoodleSyncError) as exc_info:
        MoodleSyncService().sync_user(user)

    assert "invalid JSON" in str(exc_info.value)
    assert "super-secret-token" not in str(exc_info.value)
