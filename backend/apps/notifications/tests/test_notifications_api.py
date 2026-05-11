from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.academics.models import (
    Course,
    CourseSection,
    CourseSectionStatus,
    GradingScaleBand,
)
from apps.academics.services import create_enrollment, officialise_grade, record_grade
from apps.accounts.constants import RoleCode
from apps.integration.models import IntegrationEventStatus, IntegrationOutboxEvent
from apps.integration.services import process_outbox_event
from apps.notifications.models import (
    Notification,
    NotificationCategory,
    NotificationSeverity,
)
from apps.notifications.services import create_notification
from apps.students.models import AdvisingNote, StudentProfile
from apps.testutils import authenticated_client_for_user, create_user


def create_student_profile(*, username: str = "notify-student") -> StudentProfile:
    user = create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Notify Student",
    )
    return StudentProfile.objects.create(
        user=user,
        student_number=f"2026-N-{username[-4:]}",
        national_id=f"NRC-{username}",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=2,
    )


def create_section(*, course_code: str = "CSC360", max_capacity: int = 40) -> CourseSection:
    faculty = create_user(
        username=f"faculty-{course_code.lower()}",
        email=f"faculty-{course_code.lower()}@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Faculty User",
    )
    course = Course.objects.create(
        course_code=course_code,
        course_title=f"{course_code} Title",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=max_capacity,
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
        max_capacity=max_capacity,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=21),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )


def create_authenticated_user(role: str = RoleCode.STUDENT, username: str = "notify-user"):
    user = create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=role,
        full_name=username.replace("-", " ").title(),
    )
    return user, authenticated_client_for_user(user)


def notification_paths(notification_id: str) -> list[tuple[str, str]]:
    return [
        ("get", "/api/v1/notifications"),
        ("get", "/api/v1/notifications/summary"),
        ("post", f"/api/v1/notifications/{notification_id}/read"),
        ("post", "/api/v1/notifications/read-all"),
    ]


@pytest.mark.django_db
def test_create_notification_for_user_sanitizes_metadata_and_message(settings):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.LTI_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----secret-----END PRIVATE KEY-----"
    user = create_user(username="notification-owner", email="notification-owner@example.com")

    notification = create_notification(
        recipient=user,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.WARNING,
        title="Safe title",
        message="A token super-secret-token and jwt header.payload.signature were removed.",
        metadata={
            "token": "super-secret-token",
            "raw_jwt": "header.payload.signature",
            "nested": {"private_key": "-----BEGIN PRIVATE KEY-----secret-----END PRIVATE KEY-----"},
            "safe": "value",
        },
    )

    notification.refresh_from_db()
    body = json.dumps(
        {
            "message": notification.message,
            "metadata": notification.metadata,
        }
    )
    assert notification.recipient == user
    assert notification.metadata["safe"] == "value"
    assert "super-secret-token" not in body
    assert "BEGIN PRIVATE KEY" not in body
    assert "header.payload.signature" not in body


@pytest.mark.django_db
def test_user_can_list_only_current_user_notifications():
    user, client = create_authenticated_user(username="current-owner")
    other = create_user(username="other-owner", email="other-owner@example.com")
    current_notification = create_notification(
        recipient=user,
        category=NotificationCategory.GRADES,
        severity=NotificationSeverity.SUCCESS,
        title="Grade released",
        message="Your grade is available.",
    )
    create_notification(
        recipient=other,
        category=NotificationCategory.MOODLE,
        severity=NotificationSeverity.ERROR,
        title="Other notification",
        message="This belongs to another user.",
    )

    response = client.get("/api/v1/notifications")

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == [str(current_notification.id)]
    assert data[0]["category"] == "GRADES"
    assert data[0]["severity"] == "SUCCESS"
    assert data[0]["isRead"] is False


@pytest.mark.django_db
def test_notification_summary_returns_unread_latest_and_category_counts():
    user, client = create_authenticated_user(username="summary-owner")
    create_notification(
        recipient=user,
        category=NotificationCategory.MOODLE,
        severity=NotificationSeverity.ERROR,
        title="Moodle sync failed",
        message="Sync failed safely.",
    )
    create_notification(
        recipient=user,
        category=NotificationCategory.GRADES,
        severity=NotificationSeverity.SUCCESS,
        title="Grade released",
        message="Grade available.",
        is_read=True,
    )

    response = client.get("/api/v1/notifications/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["unreadCount"] == 1
    assert data["byCategory"]["MOODLE"] == 1
    assert data["byCategory"]["GRADES"] == 1
    assert data["byCategory"]["ENROLLMENT"] == 0
    assert len(data["latest"]) == 2
    body = json.dumps(data)
    assert "metadata" not in body


@pytest.mark.django_db
def test_notification_filters_by_status_category_and_severity():
    user, client = create_authenticated_user(username="filter-owner")
    unread_moodle = create_notification(
        recipient=user,
        category=NotificationCategory.MOODLE,
        severity=NotificationSeverity.ERROR,
        title="Moodle sync failed",
        message="Sync failed safely.",
    )
    create_notification(
        recipient=user,
        category=NotificationCategory.GRADES,
        severity=NotificationSeverity.SUCCESS,
        title="Grade released",
        message="Grade available.",
        is_read=True,
    )

    response = client.get(
        "/api/v1/notifications",
        {"status": "unread", "category": "MOODLE", "severity": "ERROR"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(unread_moodle.id)]


@pytest.mark.django_db
def test_mark_one_notification_as_read_only_affects_requesting_user():
    user, client = create_authenticated_user(username="read-owner")
    other = create_user(username="read-other", email="read-other@example.com")
    current_notification = create_notification(
        recipient=user,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.INFO,
        title="System update",
        message="Review this update.",
    )
    other_notification = create_notification(
        recipient=other,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.INFO,
        title="Other update",
        message="Other user update.",
    )

    other_response = client.post(f"/api/v1/notifications/{other_notification.id}/read")
    response = client.post(f"/api/v1/notifications/{current_notification.id}/read")

    assert other_response.status_code == 404
    assert response.status_code == 200
    data = response.json()
    assert data["isRead"] is True
    assert data["readAt"] is not None
    other_notification.refresh_from_db()
    assert other_notification.is_read is False


@pytest.mark.django_db
def test_mark_all_notifications_as_read():
    user, client = create_authenticated_user(username="read-all-owner")
    create_notification(
        recipient=user,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.INFO,
        title="System update",
        message="Review this update.",
    )
    create_notification(
        recipient=user,
        category=NotificationCategory.ENROLLMENT,
        severity=NotificationSeverity.SUCCESS,
        title="Enrollment confirmed",
        message="Enrollment confirmed.",
    )

    response = client.post("/api/v1/notifications/read-all")

    assert response.status_code == 200
    assert response.json()["updatedCount"] == 2
    assert Notification.objects.filter(recipient=user, is_read=False).count() == 0


@pytest.mark.django_db
def test_unauthenticated_requests_are_rejected():
    user = create_user(username="unauth-owner", email="unauth-owner@example.com")
    notification = create_notification(
        recipient=user,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.INFO,
        title="System update",
        message="Review this update.",
    )

    for method, path in notification_paths(str(notification.id)):
        response = getattr(APIClient(), method)(path)
        assert response.status_code == 401, path


@pytest.mark.django_db
def test_moodle_sync_failure_creates_admin_notification_without_secrets(settings, monkeypatch):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.LTI_PRIVATE_KEY = "private-key-secret"
    admin = create_user(
        username="moodle-notify-admin",
        email="moodle-notify-admin@example.com",
        primary_role=RoleCode.ADMIN,
        full_name="Moodle Notify Admin",
    )
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": admin.id, "raw_jwt": "unsafe.jwt.token"},
    )

    def fail_sync(self, failed_event):
        raise RuntimeError("Moodle rejected token super-secret-token and private-key-secret")

    monkeypatch.setattr("apps.integration.services.MoodleSyncService.process_event", fail_sync)

    result = process_outbox_event(event.id)

    assert result is False
    event.refresh_from_db()
    assert event.status == IntegrationEventStatus.FAILED
    notification = Notification.objects.get(recipient=admin, category=NotificationCategory.MOODLE)
    assert notification.severity == NotificationSeverity.ERROR
    assert notification.title == "Moodle sync failed"
    assert notification.action_url == "/admin/moodle-sync"
    assert notification.source_type == "IntegrationOutboxEvent"
    assert notification.source_id == str(event.id)
    body = json.dumps({"message": notification.message, "metadata": notification.metadata})
    assert "super-secret-token" not in body
    assert "private-key-secret" not in body
    assert "unsafe.jwt.token" not in body


@pytest.mark.django_db
def test_enrollment_confirmed_creates_student_notification():
    student = create_student_profile(username="enroll-notify-student")
    section = create_section(course_code="CSC361")

    enrollment = create_enrollment(
        student=student,
        section=section,
        actor_user=student.user,
        actor_role=RoleCode.STUDENT,
    )

    notification = Notification.objects.get(recipient=student.user, source_id=str(enrollment.id))
    assert notification.category == NotificationCategory.ENROLLMENT
    assert notification.severity == NotificationSeverity.SUCCESS
    assert notification.title == "Enrollment confirmed"
    assert notification.action_url == "/student/courses"


@pytest.mark.django_db
def test_grade_officialised_creates_student_notification():
    student = create_student_profile(username="grade-notify-student")
    section = create_section(course_code="CSC362")
    GradingScaleBand.objects.create(
        letter_grade="A",
        minimum_score=Decimal("80.00"),
        maximum_score=Decimal("100.00"),
        grade_points=Decimal("4.00"),
        display_order=1,
    )
    create_enrollment(
        student=student,
        section=section,
        actor_user=student.user,
        actor_role=RoleCode.STUDENT,
    )
    grade_record = record_grade(
        student=student,
        section=section,
        actor_user=section.faculty_user,
        numeric_score=Decimal("88.00"),
    )

    officialise_grade(grade_record=grade_record, actor_user=section.faculty_user)

    notification = Notification.objects.get(recipient=student.user, source_id=str(grade_record.id))
    assert notification.category == NotificationCategory.GRADES
    assert notification.severity == NotificationSeverity.SUCCESS
    assert notification.title == "Grade released"
    assert notification.action_url == "/student/grades"


@pytest.mark.django_db
def test_approved_advising_note_creates_student_notification_without_note_text():
    admin, admin_client = create_authenticated_user(role=RoleCode.ADMIN, username="advising-note-admin")
    advisor = create_user(
        username="advising-note-advisor",
        email="advising-note-advisor@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Advising Note Advisor",
    )
    student = create_student_profile(username="advising-notify-student")
    note = AdvisingNote.objects.create(
        student=student,
        created_by_user=advisor,
        note_text="Sensitive advising text should not appear in notification payloads.",
    )

    response = admin_client.post(f"/api/v1/students/{student.id}/advising-notes/{note.id}/approve")

    assert response.status_code == 200
    notification = Notification.objects.get(recipient=student.user, source_id=str(note.id))
    assert notification.category == NotificationCategory.ADVISING
    assert notification.severity == NotificationSeverity.INFO
    assert notification.title == "Advising note available"
    assert notification.action_url == "/student"
    body = json.dumps({"message": notification.message, "metadata": notification.metadata})
    assert "Sensitive advising text" not in body
    note.refresh_from_db()
    assert note.approved_by_user_id == admin.id
