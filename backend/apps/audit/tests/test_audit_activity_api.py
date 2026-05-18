from __future__ import annotations

import json
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.integration.models import IntegrationEventStatus, IntegrationOutboxEvent
from apps.integration.services import process_outbox_event
from apps.notifications.models import NotificationCategory, NotificationSeverity
from apps.notifications.services import create_notification
from apps.testutils import authenticated_client_for_user, create_user

from apps.audit.models import AuditCategory, AuditEvent, AuditSeverity
from apps.audit.services import record_audit_event, sanitize_audit_metadata


def create_admin_client(username: str = "audit-admin") -> APIClient:
    admin = create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Audit Admin",
    )
    return authenticated_client_for_user(admin)


def create_actor(role: str = RoleCode.ADMIN, username: str = "activity-actor"):
    return create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=role,
        full_name=username.replace("-", " ").title(),
    )


def admin_activity_paths(event_id: str) -> list[tuple[str, str]]:
    return [
        ("get", "/api/v1/admin/activity"),
        ("get", "/api/v1/admin/activity/summary"),
        ("get", f"/api/v1/admin/activity/{event_id}"),
    ]


@pytest.mark.django_db
def test_admin_can_list_activity_with_safe_metadata(settings):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.LTI_PRIVATE_KEY = "private-key-secret"
    actor = create_actor(username="list-actor")
    event = record_audit_event(
        actor=actor,
        category=AuditCategory.MOODLE,
        action="MOODLE_SYNC_FAILED",
        summary="Moodle sync failed for token super-secret-token.",
        target_type="IntegrationOutboxEvent",
        target_id="event-123",
        severity=AuditSeverity.ERROR,
        metadata={
            "eventType": "GRADE_SYNC_REQUESTED",
            "safeError": "JWT eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.signature and private-key-secret were removed.",
            "token": "super-secret-token",
        },
    )

    response = create_admin_client().get("/api/v1/admin/activity")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["id"] == str(event.id)
    assert data[0]["actor"]["username"] == actor.username
    assert data[0]["category"] == "MOODLE"
    assert data[0]["action"] == "MOODLE_SYNC_FAILED"
    assert data[0]["severity"] == "ERROR"
    assert data[0]["targetType"] == "IntegrationOutboxEvent"
    body = json.dumps(data)
    assert "super-secret-token" not in body
    assert "private-key-secret" not in body
    assert "eyJhbGciOiJIUzI1NiJ9" not in body


@pytest.mark.django_db
def test_admin_can_fetch_summary_with_category_counts():
    record_audit_event(category=AuditCategory.USER, action="USER_CREATED", summary="User created.", severity=AuditSeverity.SUCCESS)
    record_audit_event(category=AuditCategory.MOODLE, action="MOODLE_SYNC_FAILED", summary="Sync failed.", severity=AuditSeverity.ERROR)
    record_audit_event(category=AuditCategory.NOTIFICATION, action="NOTIFICATION_READ", summary="Notification read.", severity=AuditSeverity.INFO)
    yesterday = record_audit_event(
        category=AuditCategory.SYSTEM,
        action="SYSTEM_NOTE",
        summary="Older event.",
        severity=AuditSeverity.WARNING,
    )
    AuditEvent.objects.filter(id=yesterday.id).update(created_at=timezone.now() - timedelta(days=1, minutes=5))

    response = create_admin_client().get("/api/v1/admin/activity/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["errors"] == 1
    assert data["warnings"] == 1
    assert data["today"] == 3
    assert data["byCategory"]["USER"] == 1
    assert data["byCategory"]["MOODLE"] == 1
    assert data["byCategory"]["NOTIFICATION"] == 1


@pytest.mark.django_db
def test_filters_work_by_category_severity_action_search_and_date_range():
    actor = create_actor(username="filter-actor")
    matching = record_audit_event(
        actor=actor,
        category=AuditCategory.GRADE,
        action="GRADE_OFFICIALISED",
        summary="Official grade released for target 777.",
        target_type="GradeRecord",
        target_id="grade-777",
        severity=AuditSeverity.SUCCESS,
    )
    old_event = record_audit_event(
        actor=create_actor(username="old-actor"),
        category=AuditCategory.MOODLE,
        action="MOODLE_SYNC_FAILED",
        summary="Old Moodle failure.",
        target_id="old-target",
        severity=AuditSeverity.ERROR,
    )
    AuditEvent.objects.filter(id=old_event.id).update(created_at=timezone.now() - timedelta(days=5))

    response = create_admin_client().get(
        "/api/v1/admin/activity",
        {
            "category": "GRADE",
            "severity": "SUCCESS",
            "action": "GRADE_OFFICIALISED",
            "search": "target 777",
            "date_from": (timezone.now() - timedelta(days=1)).date().isoformat(),
            "date_to": (timezone.now() + timedelta(days=1)).date().isoformat(),
        },
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(matching.id)]


@pytest.mark.django_db
def test_admin_can_fetch_detail_with_redacted_metadata(settings):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    event = record_audit_event(
        category=AuditCategory.SYSTEM,
        action="SYSTEM_SAFE_CHECK",
        summary="Checked authorization header.",
        severity=AuditSeverity.INFO,
        metadata={
            "password": "do-not-return",
            "authorization": "Bearer super-secret-token",
            "nested": {
                "wstoken": "super-secret-token",
                "access": "access-secret",
                "refresh": "refresh-secret",
            },
            "safe": "value",
        },
    )

    response = create_admin_client().get(f"/api/v1/admin/activity/{event.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["safe"] == "value"
    body = json.dumps(data)
    assert "do-not-return" not in body
    assert "super-secret-token" not in body
    assert "access-secret" not in body
    assert "refresh-secret" not in body
    assert "authorization" in body


@pytest.mark.django_db
def test_metadata_sanitizer_redacts_secret_keys_and_jwt_like_values(settings):
    settings.LTI_PRIVATE_KEY = "private-key-secret"
    sanitized = sanitize_audit_metadata(
        {
            "token": "abc123",
            "password": "password123",
            "private_key": "private-key-secret",
            "raw_jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.signature",
            "safe": "visible",
            "nested": {"refresh_token": "refresh-secret", "access": "access-secret"},
        }
    )

    body = json.dumps(sanitized)
    assert sanitized["safe"] == "visible"
    assert "abc123" not in body
    assert "password123" not in body
    assert "private-key-secret" not in body
    assert "eyJhbGciOiJIUzI1NiJ9" not in body
    assert "refresh-secret" not in body
    assert "access-secret" not in body


@pytest.mark.django_db
def test_unauthenticated_requests_are_rejected():
    event = record_audit_event(category=AuditCategory.SYSTEM, action="SYSTEM_NOTE", summary="System note.")

    for method, path in admin_activity_paths(str(event.id)):
        response = getattr(APIClient(), method)(path)
        assert response.status_code == 401, path


@pytest.mark.parametrize("role", [RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.FACULTY])
@pytest.mark.django_db
def test_non_admin_requests_are_forbidden(role):
    event = record_audit_event(category=AuditCategory.SYSTEM, action="SYSTEM_NOTE", summary="System note.")
    user = create_actor(role=role, username=f"audit-denied-{role.lower()}")
    client = authenticated_client_for_user(user)

    for method, path in admin_activity_paths(str(event.id)):
        response = getattr(client, method)(path)
        assert response.status_code == 403, path


@pytest.mark.django_db
def test_moodle_sync_failure_creates_audit_event_without_secrets(settings, monkeypatch):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.LTI_PRIVATE_KEY = "private-key-secret"
    create_actor(role=RoleCode.ADMIN, username="audit-moodle-admin")
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": 12, "raw_jwt": "unsafe.jwt.token"},
    )

    def fail_sync(self, failed_event):
        raise RuntimeError("Moodle rejected token super-secret-token and private-key-secret")

    monkeypatch.setattr("apps.integration.services.MoodleSyncService.process_event", fail_sync)

    result = process_outbox_event(event.id)

    assert result is False
    event.refresh_from_db()
    assert event.status == IntegrationEventStatus.FAILED
    audit_event = AuditEvent.objects.get(target_id=str(event.id), action="MOODLE_SYNC_FAILED")
    assert audit_event.category == AuditCategory.MOODLE
    assert audit_event.severity == AuditSeverity.ERROR
    body = json.dumps({"summary": audit_event.summary, "metadata": audit_event.metadata})
    assert "super-secret-token" not in body
    assert "private-key-secret" not in body
    assert "unsafe.jwt.token" not in body


@pytest.mark.django_db
def test_notification_read_creates_audit_event():
    user = create_actor(role=RoleCode.STUDENT, username="audit-notification-owner")
    client = authenticated_client_for_user(user)
    notification = create_notification(
        recipient=user,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.INFO,
        title="System update",
        message="Review this update.",
    )

    response = client.post(f"/api/v1/notifications/{notification.id}/read")

    assert response.status_code == 200
    audit_event = AuditEvent.objects.get(target_id=str(notification.id), action="NOTIFICATION_READ")
    assert audit_event.actor == user
    assert audit_event.category == AuditCategory.NOTIFICATION
    assert audit_event.severity == AuditSeverity.INFO


@pytest.mark.django_db
def test_seed_audit_activity_demo_creates_safe_idempotent_demo_records():
    create_actor(role=RoleCode.ADMIN, username="audit-demo-admin")

    call_command("seed_audit_activity_demo")
    call_command("seed_audit_activity_demo")

    demo_events = AuditEvent.objects.filter(metadata__demo=True)
    assert demo_events.count() == 5
    assert set(demo_events.values_list("category", flat=True)) == {
        AuditCategory.USER,
        AuditCategory.MOODLE,
        AuditCategory.NOTIFICATION,
        AuditCategory.LTI,
        AuditCategory.SYSTEM,
    }
    body = json.dumps(list(demo_events.values("summary", "metadata")))
    assert "super-secret-token" not in body
    assert "private-key-secret" not in body
    assert "eyJhbGciOiJIUzI1NiJ9" not in body
