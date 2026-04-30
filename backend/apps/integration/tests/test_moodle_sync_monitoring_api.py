from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.academics.models import Course, CourseSection, CourseSectionStatus
from apps.accounts.constants import RoleCode
from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.students.models import StudentProfile
from apps.testutils import authenticated_client_for_user, create_user


def create_admin_client() -> APIClient:
    admin = create_user(
        username="monitor-admin",
        email="monitor-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Monitor Admin",
    )
    return authenticated_client_for_user(admin)


def create_section(*, course_code: str = "CSC350") -> CourseSection:
    faculty = create_user(
        username=f"faculty-{course_code.lower()}",
        email=f"faculty-{course_code.lower()}@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Course Faculty",
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
    return CourseSection.objects.create(
        course=course,
        section_code="A1",
        faculty_user=faculty,
        room="LT-1",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=50,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=21),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )


def create_student_profile(*, username: str = "mapped-student") -> StudentProfile:
    user = create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Mapped Student",
    )
    return StudentProfile.objects.create(
        user=user,
        student_number=f"2026-CS-{username[-3:]}",
        national_id=f"NRC-{username}",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=3,
    )


def monitoring_endpoint_paths(event_id: str) -> list[tuple[str, str]]:
    return [
        ("get", "/api/v1/integration/moodle/summary"),
        ("get", "/api/v1/integration/moodle/outbox-events"),
        ("post", f"/api/v1/integration/moodle/outbox-events/{event_id}/retry"),
        ("get", "/api/v1/integration/moodle/user-maps"),
        ("get", "/api/v1/integration/moodle/course-maps"),
        ("get", "/api/v1/integration/moodle/engagement-runs"),
        ("get", "/api/v1/integration/moodle/engagement-snapshots"),
    ]


@pytest.mark.django_db
def test_admin_can_fetch_summary_with_counts_and_without_secrets(settings):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.LTI_CLIENT_ID = "local-client"
    settings.LTI_DEPLOYMENT_ID = "local-deployment"
    settings.LTI_PLATFORM_ISSUER_ALLOWLIST = ["https://moodle.example.test"]
    settings.LTI_PRIVATE_KEY = "private-key-secret"
    settings.LTI_PUBLIC_KEY = "public-key"

    pending = IntegrationOutboxEvent.objects.create(event_type="USER_SYNC_REQUESTED", payload={"user_id": 101})
    IntegrationOutboxEvent.objects.create(
        event_type="COURSE_SYNC_REQUESTED",
        payload={"section_id": "section-1"},
        status=IntegrationEventStatus.PROCESSED,
    )
    IntegrationOutboxEvent.objects.create(
        event_type="GRADE_SYNC_REQUESTED",
        payload={"grade_id": "grade-1"},
        status=IntegrationEventStatus.FAILED,
        attempts=2,
        last_error="safe failure",
    )
    user = create_user(username="moodle-map-user", email="moodle-map-user@example.com")
    MoodleUserMap.objects.create(user=user, moodle_user_id=5001, moodle_username=user.username)
    section = create_section()
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=8801,
        moodle_shortname="CSC350-A1",
        moodle_category_id=7,
    )
    run = MoodleEngagementIngestionRun.objects.create(
        status=MoodleEngagementIngestionStatus.SUCCEEDED,
        completed_at=timezone.now(),
        snapshots_created=3,
        snapshots_updated=2,
        failure_count=0,
    )

    response = create_admin_client().get("/api/v1/integration/moodle/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["outbox"] == {"pending": 1, "processed": 1, "failed": 1, "retryable": 2}
    assert data["mappings"] == {"users": 1, "courses": 1}
    assert data["engagement"]["latestRunStatus"] == run.status
    assert data["engagement"]["latestRunSnapshots"] == 5
    assert data["readiness"] == {"moodleRestConfig": "present", "ltiConfig": "present"}
    body = json.dumps(data)
    assert str(pending.id) not in body
    assert "super-secret-token" not in body
    assert "private-key-secret" not in body


@pytest.mark.django_db
def test_unauthenticated_user_cannot_fetch_summary():
    response = APIClient().get("/api/v1/integration/moodle/summary")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.FACULTY])
@pytest.mark.django_db
def test_non_admin_users_cannot_fetch_summary(role):
    user = create_user(
        username=f"monitor-{role.lower()}",
        email=f"monitor-{role.lower()}@example.com",
        password="Secret123!",
        primary_role=role,
    )
    client = authenticated_client_for_user(user)

    response = client.get("/api/v1/integration/moodle/summary")

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_list_outbox_events_with_filters_and_safe_payload_summary(settings):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    matching = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={
            "user_id": 42,
            "wstoken": "super-secret-token",
            "raw_jwt": "unsafe-token",
            "nested": {"secret": "do-not-return"},
        },
        status=IntegrationEventStatus.FAILED,
        attempts=2,
        last_error="safe sync error",
    )
    IntegrationOutboxEvent.objects.create(
        event_type="COURSE_SYNC_REQUESTED",
        payload={"section_id": "section-99"},
        status=IntegrationEventStatus.PENDING,
    )

    response = create_admin_client().get(
        "/api/v1/integration/moodle/outbox-events",
        {"status": "FAILED", "event_type": "USER_SYNC_REQUESTED", "search": "42"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(matching.id)
    assert data[0]["eventType"] == "USER_SYNC_REQUESTED"
    assert data[0]["status"] == "FAILED"
    assert data[0]["payloadSummary"] == {
        "userId": 42,
        "sectionId": None,
        "enrollmentId": None,
        "studentId": None,
        "gradeId": None,
        "action": "",
    }
    assert data[0]["canRetry"] is True
    body = json.dumps(data)
    assert "super-secret-token" not in body
    assert "unsafe-token" not in body
    assert "do-not-return" not in body


@pytest.mark.django_db
def test_admin_can_retry_failed_outbox_event(monkeypatch):
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": 42},
        status=IntegrationEventStatus.FAILED,
        attempts=1,
        last_error="previous failure",
    )

    def fake_process_outbox_event(event_id):
        IntegrationOutboxEvent.objects.filter(id=event_id).update(
            status=IntegrationEventStatus.PROCESSED,
            attempts=2,
            last_error="",
            processed_at=timezone.now(),
            last_attempt_at=timezone.now(),
        )
        return True

    monkeypatch.setattr("apps.integration.api.views.process_outbox_event", fake_process_outbox_event)

    response = create_admin_client().post(f"/api/v1/integration/moodle/outbox-events/{event.id}/retry")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(event.id)
    assert data["status"] == "PROCESSED"
    assert data["canRetry"] is False


@pytest.mark.django_db
def test_retrying_processed_outbox_event_is_rejected_safely():
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": 42},
        status=IntegrationEventStatus.PROCESSED,
    )

    response = create_admin_client().post(f"/api/v1/integration/moodle/outbox-events/{event.id}/retry")

    assert response.status_code == 400
    body = json.dumps(response.json())
    assert "cannot be retried" in body
    assert "payload" not in body.lower()


@pytest.mark.django_db
def test_retry_failure_returns_safe_error_without_token(settings, monkeypatch):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": 42},
        status=IntegrationEventStatus.FAILED,
        attempts=1,
    )

    def fake_process_outbox_event(event_id):
        IntegrationOutboxEvent.objects.filter(id=event_id).update(
            status=IntegrationEventStatus.FAILED,
            attempts=2,
            last_error="safe retry failure",
            last_attempt_at=timezone.now(),
        )
        return False

    monkeypatch.setattr("apps.integration.api.views.process_outbox_event", fake_process_outbox_event)

    response = create_admin_client().post(f"/api/v1/integration/moodle/outbox-events/{event.id}/retry")

    assert response.status_code == 502
    body = json.dumps(response.json())
    assert "safe retry failure" in body
    assert "super-secret-token" not in body


@pytest.mark.django_db
def test_admin_can_list_user_maps():
    user = create_user(
        username="mapped-user",
        email="mapped-user@example.com",
        primary_role=RoleCode.STUDENT,
        full_name="Mapped User",
    )
    mapping = MoodleUserMap.objects.create(user=user, moodle_user_id=5001, moodle_username="mapped-user")

    response = create_admin_client().get("/api/v1/integration/moodle/user-maps")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(mapping.id)
    assert response.json()[0]["sisUser"]["fullName"] == "Mapped User"
    assert response.json()[0]["moodleUserId"] == 5001


@pytest.mark.django_db
def test_admin_can_list_course_maps():
    section = create_section(course_code="CSC351")
    mapping = MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=8802,
        moodle_shortname="CSC351-A1",
        moodle_category_id=7,
        grade_component="FINAL",
        grade_activity_id=901,
        grade_item_number=0,
    )

    response = create_admin_client().get("/api/v1/integration/moodle/course-maps")

    assert response.status_code == 200
    data = response.json()[0]
    assert data["id"] == str(mapping.id)
    assert data["sisSection"]["courseCode"] == "CSC351"
    assert data["moodleCourseId"] == 8802
    assert data["gradeTargetConfigured"] is True


@pytest.mark.django_db
def test_admin_can_list_engagement_runs_and_snapshots():
    student = create_student_profile(username="snap-student")
    user = student.user
    section = create_section(course_code="CSC352")
    run = MoodleEngagementIngestionRun.objects.create(
        status=MoodleEngagementIngestionStatus.PARTIAL,
        dry_run=False,
        completed_at=timezone.now(),
        courses_inspected=1,
        users_inspected=1,
        snapshots_created=1,
        failure_count=1,
        last_error="safe partial error",
    )
    snapshot = MoodleEngagementSnapshot.objects.create(
        run=run,
        user=user,
        student=student,
        section=section,
        moodle_user_id=5501,
        moodle_course_id=8803,
        moodle_last_access_at=timezone.now(),
        moodle_course_last_access_at=timezone.now(),
        collected_at=timezone.now(),
    )
    client = create_admin_client()

    runs_response = client.get("/api/v1/integration/moodle/engagement-runs")
    snapshots_response = client.get("/api/v1/integration/moodle/engagement-snapshots")

    assert runs_response.status_code == 200
    assert runs_response.json()[0]["id"] == str(run.id)
    assert runs_response.json()[0]["status"] == "PARTIAL"
    assert runs_response.json()[0]["snapshotsTotal"] == 1
    assert snapshots_response.status_code == 200
    assert snapshots_response.json()[0]["id"] == str(snapshot.id)
    assert snapshots_response.json()[0]["studentUser"]["username"] == user.username
    assert snapshots_response.json()[0]["section"]["courseCode"] == "CSC352"


@pytest.mark.parametrize("role", [RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.FACULTY])
@pytest.mark.django_db
def test_non_admin_access_is_denied_for_all_monitoring_endpoints(role):
    event = IntegrationOutboxEvent.objects.create(event_type="USER_SYNC_REQUESTED", payload={"user_id": 42})
    user = create_user(
        username=f"denied-{role.lower()}",
        email=f"denied-{role.lower()}@example.com",
        password="Secret123!",
        primary_role=role,
    )
    client = authenticated_client_for_user(user)

    for method, path in monitoring_endpoint_paths(str(event.id)):
        response = getattr(client, method)(path)
        assert response.status_code == 403, path
