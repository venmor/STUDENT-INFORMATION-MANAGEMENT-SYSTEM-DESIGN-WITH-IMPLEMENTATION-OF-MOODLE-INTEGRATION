from __future__ import annotations

import json
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditCategory, AuditEvent
from apps.testutils import authenticated_client_for_user, create_user


def create_role_user(role: str, username: str):
    return create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=role,
        full_name=username.replace("-", " ").title(),
    )


def event_payload(**overrides):
    start_at = timezone.now() + timedelta(days=10)
    payload = {
        "title": "Registration Deadline",
        "description": "Last day to register for Semester 1 courses.",
        "eventType": "REGISTRATION_DEADLINE",
        "audience": "STUDENTS",
        "priority": "HIGH",
        "academicYear": "2026/2027",
        "semester": "Semester 1",
        "startAt": start_at.isoformat().replace("+00:00", "Z"),
        "endAt": None,
        "allDay": False,
        "location": "",
        "status": "ACTIVE",
        "source": "MANUAL",
        "metadata": {"safe": "value"},
    }
    payload.update(overrides)
    return payload


def create_event(client, **overrides):
    response = client.post("/api/v1/calendar/events/", event_payload(**overrides), format="json")
    assert response.status_code == 201, response.json()
    return response.json()


@pytest.mark.django_db
def test_admin_can_list_all_events_and_students_only_see_their_audience():
    admin = create_role_user(RoleCode.ADMIN, "calendar-admin")
    student = create_role_user(RoleCode.STUDENT, "calendar-student")
    admin_client = authenticated_client_for_user(admin)
    student_client = authenticated_client_for_user(student)

    student_event = create_event(admin_client, title="Student deadline", audience="STUDENTS")
    faculty_event = create_event(admin_client, title="Faculty deadline", audience="FACULTY", eventType="GRADE_SUBMISSION_DEADLINE")
    all_event = create_event(admin_client, title="Term starts", audience="ALL", eventType="TERM_START")
    draft_event = create_event(admin_client, title="Draft admin planning", audience="ADMINS", status="DRAFT")

    admin_response = admin_client.get("/api/v1/calendar/events/")
    student_response = student_client.get("/api/v1/calendar/events/")

    assert admin_response.status_code == 200
    assert {item["id"] for item in admin_response.json()} == {
        student_event["id"],
        faculty_event["id"],
        all_event["id"],
        draft_event["id"],
    }
    assert student_response.status_code == 200
    assert {item["id"] for item in student_response.json()} == {student_event["id"], all_event["id"]}


@pytest.mark.parametrize(
    ("role", "visible_audience", "hidden_audience"),
    [
        (RoleCode.FACULTY, "FACULTY", "STUDENTS"),
        (RoleCode.ADVISOR, "ADVISORS", "FACULTY"),
    ],
)
@pytest.mark.django_db
def test_faculty_and_advisor_visibility(role, visible_audience, hidden_audience):
    admin = create_role_user(RoleCode.ADMIN, f"admin-{role.lower()}")
    user = create_role_user(role, f"user-{role.lower()}")
    admin_client = authenticated_client_for_user(admin)
    client = authenticated_client_for_user(user)

    visible = create_event(admin_client, title=f"{visible_audience} date", audience=visible_audience)
    shared = create_event(admin_client, title="Shared date", audience="ALL", eventType="TERM_START")
    create_event(admin_client, title="Hidden date", audience=hidden_audience, eventType="GENERAL")

    response = client.get("/api/v1/calendar/events/")

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {visible["id"], shared["id"]}


@pytest.mark.django_db
def test_admin_can_create_update_and_cancel_event_with_audit_records():
    admin = create_role_user(RoleCode.ADMIN, "calendar-audit-admin")
    client = authenticated_client_for_user(admin)

    created = create_event(client, title="Grade submission deadline", eventType="GRADE_SUBMISSION_DEADLINE", audience="FACULTY")
    update_response = client.patch(
        f"/api/v1/calendar/events/{created['id']}/",
        {"title": "Updated grade submission deadline", "priority": "CRITICAL"},
        format="json",
    )
    cancel_response = client.post(f"/api/v1/calendar/events/{created['id']}/cancel/", {}, format="json")

    assert update_response.status_code == 200, update_response.json()
    assert update_response.json()["title"] == "Updated grade submission deadline"
    assert update_response.json()["priority"] == "CRITICAL"
    assert cancel_response.status_code == 200, cancel_response.json()
    assert cancel_response.json()["status"] == "CANCELLED"

    actions = set(AuditEvent.objects.filter(target_id=created["id"]).values_list("action", flat=True))
    assert actions == {
        "ACADEMIC_CALENDAR_EVENT_CREATED",
        "ACADEMIC_CALENDAR_EVENT_UPDATED",
        "ACADEMIC_CALENDAR_EVENT_CANCELLED",
    }
    assert AuditEvent.objects.filter(target_id=created["id"], category=AuditCategory.ACADEMIC_CALENDAR).count() == 3


@pytest.mark.django_db
def test_non_admin_cannot_create_or_update_and_unauthenticated_gets_401():
    admin = create_role_user(RoleCode.ADMIN, "calendar-permission-admin")
    student = create_role_user(RoleCode.STUDENT, "calendar-permission-student")
    admin_client = authenticated_client_for_user(admin)
    student_client = authenticated_client_for_user(student)
    created = create_event(admin_client)

    create_response = student_client.post("/api/v1/calendar/events/", event_payload(title="Not allowed"), format="json")
    update_response = student_client.patch(f"/api/v1/calendar/events/{created['id']}/", {"title": "Not allowed"}, format="json")
    unauthenticated_response = APIClient().get("/api/v1/calendar/events/")

    assert create_response.status_code == 403
    assert update_response.status_code == 403
    assert unauthenticated_response.status_code == 401


@pytest.mark.django_db
def test_invalid_end_date_and_missing_required_text_are_rejected():
    admin = create_role_user(RoleCode.ADMIN, "calendar-validation-admin")
    client = authenticated_client_for_user(admin)
    start_at = timezone.now() + timedelta(days=5)
    end_at = start_at - timedelta(hours=1)

    invalid_end = client.post(
        "/api/v1/calendar/events/",
        event_payload(
            startAt=start_at.isoformat().replace("+00:00", "Z"),
            endAt=end_at.isoformat().replace("+00:00", "Z"),
        ),
        format="json",
    )
    missing_title = client.post("/api/v1/calendar/events/", event_payload(title=""), format="json")
    missing_year = client.post("/api/v1/calendar/events/", event_payload(academicYear=""), format="json")
    missing_semester = client.post("/api/v1/calendar/events/", event_payload(semester=""), format="json")

    assert invalid_end.status_code == 400
    assert "endAt" in invalid_end.json()
    assert missing_title.status_code == 400
    assert missing_year.status_code == 400
    assert missing_semester.status_code == 400


@pytest.mark.django_db
def test_filters_work_by_type_audience_date_range_semester_year_and_status():
    admin = create_role_user(RoleCode.ADMIN, "calendar-filter-admin")
    client = authenticated_client_for_user(admin)
    matching_start = timezone.now() + timedelta(days=3)
    create_event(
        client,
        title="Matching exam",
        eventType="EXAM_PERIOD",
        audience="STUDENTS",
        semester="Semester 2",
        academicYear="2026/2027",
        status="ACTIVE",
        startAt=matching_start.isoformat().replace("+00:00", "Z"),
    )
    create_event(client, title="Wrong type", eventType="GENERAL", audience="STUDENTS", semester="Semester 2")
    create_event(client, title="Wrong status", eventType="EXAM_PERIOD", audience="STUDENTS", semester="Semester 2", status="DRAFT")

    response = client.get(
        "/api/v1/calendar/events/",
        {
            "event_type": "EXAM_PERIOD",
            "audience": "STUDENTS",
            "semester": "Semester 2",
            "academic_year": "2026/2027",
            "status": "ACTIVE",
            "start": (matching_start - timedelta(days=1)).date().isoformat(),
            "end": (matching_start + timedelta(days=1)).date().isoformat(),
        },
    )

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Matching exam"]


@pytest.mark.django_db
def test_summary_endpoint_returns_counts_current_term_and_next_event():
    admin = create_role_user(RoleCode.ADMIN, "calendar-summary-admin")
    student = create_role_user(RoleCode.STUDENT, "calendar-summary-student")
    admin_client = authenticated_client_for_user(admin)
    student_client = authenticated_client_for_user(student)
    now = timezone.now()
    next_start = now + timedelta(days=2)

    next_event = create_event(
        admin_client,
        title="Next registration deadline",
        eventType="REGISTRATION_DEADLINE",
        audience="STUDENTS",
        startAt=next_start.isoformat().replace("+00:00", "Z"),
    )
    create_event(admin_client, title="Exam period", eventType="EXAM_PERIOD", audience="ALL", startAt=(now + timedelta(days=10)).isoformat().replace("+00:00", "Z"))
    create_event(admin_client, title="Grade deadline", eventType="GRADE_SUBMISSION_DEADLINE", audience="FACULTY", startAt=(now + timedelta(days=12)).isoformat().replace("+00:00", "Z"))

    response = student_client.get("/api/v1/calendar/summary/")

    assert response.status_code == 200
    data = response.json()
    assert data["upcomingCount"] == 2
    assert data["registrationDeadlines"] == 1
    assert data["examPeriods"] == 1
    assert data["gradeDeadlines"] == 0
    assert data["currentAcademicYear"] == "2026/2027"
    assert data["currentSemester"] == "Semester 1"
    assert data["nextEvent"]["id"] == next_event["id"]
    assert data["nextEvent"]["title"] == "Next registration deadline"
    assert data["nextEvent"]["startAt"] == next_event["startAt"]


@pytest.mark.django_db
def test_urgency_labels_are_returned_for_events():
    admin = create_role_user(RoleCode.ADMIN, "calendar-urgency-admin")
    client = authenticated_client_for_user(admin)
    now = timezone.now()
    overdue = create_event(client, title="Overdue deadline", startAt=(now - timedelta(days=1)).isoformat().replace("+00:00", "Z"))
    today = create_event(client, title="Today deadline", startAt=now.isoformat().replace("+00:00", "Z"))
    this_week = create_event(client, title="This week deadline", startAt=(now + timedelta(days=4)).isoformat().replace("+00:00", "Z"))
    upcoming = create_event(client, title="Upcoming deadline", startAt=(now + timedelta(days=20)).isoformat().replace("+00:00", "Z"))
    future = create_event(client, title="Future deadline", startAt=(now + timedelta(days=45)).isoformat().replace("+00:00", "Z"))

    response = client.get("/api/v1/calendar/events/")
    labels = {item["id"]: item["urgency"] for item in response.json()}

    assert labels[overdue["id"]] == "OVERDUE"
    assert labels[today["id"]] == "TODAY"
    assert labels[this_week["id"]] == "THIS_WEEK"
    assert labels[upcoming["id"]] == "UPCOMING"
    assert labels[future["id"]] == "FUTURE"


@pytest.mark.django_db
def test_calendar_metadata_and_api_output_redact_secrets(settings):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    admin = create_role_user(RoleCode.ADMIN, "calendar-redact-admin")
    client = authenticated_client_for_user(admin)

    created = create_event(
        client,
        metadata={
            "safe": "visible",
            "token": "super-secret-token",
            "nested": {"rawJwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.signature"},
        },
    )
    detail_response = client.get(f"/api/v1/calendar/events/{created['id']}/")

    assert detail_response.status_code == 200
    body = json.dumps(detail_response.json())
    assert "visible" in body
    assert "super-secret-token" not in body
    assert "eyJhbGciOiJIUzI1NiJ9" not in body
