from io import StringIO
from unittest.mock import Mock

from django.core.management import call_command

from apps.accounts.constants import RoleCode
from apps.integration.models import IntegrationEventStatus, IntegrationOutboxEvent
from apps.testutils import create_user


def test_process_moodle_sync_command_retries_failed_event(settings, monkeypatch, db):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.MOODLE_DEFAULT_CATEGORY_ID = 7
    settings.MOODLE_STUDENT_ROLE_ID = 5
    settings.MOODLE_EDITING_TEACHER_ROLE_ID = 3
    settings.MOODLE_INSTITUTION = "Student Information System"
    settings.MOODLE_GRADE_SOURCE = "modern_sis"
    stdout = StringIO()

    user = create_user(
        username="retry-user",
        email="retry-user@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Retry User",
    )
    event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": user.id, "action": "UPSERT"},
        status=IntegrationEventStatus.FAILED,
        attempts=1,
        last_error="previous error",
    )
    post_mock = Mock(
        side_effect=[
            Mock(**{"raise_for_status.side_effect": None, "json.return_value": [{"id": 99, "username": "retry-user"}]}),
            Mock(**{"raise_for_status.side_effect": None, "json.return_value": {"users": [{"id": 99, "username": "retry-user"}]}}),
        ]
    )
    monkeypatch.setattr("requests.post", post_mock)

    call_command("process_moodle_sync", "--failed", stdout=stdout)

    event.refresh_from_db()
    assert event.status == IntegrationEventStatus.PROCESSED
    assert event.attempts == 2
    assert "processed=1" in stdout.getvalue()


def test_process_moodle_sync_command_can_scope_to_single_event(settings, monkeypatch, db):
    settings.MOODLE_BASE_URL = "https://moodle.example.test"
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    settings.MOODLE_DEFAULT_CATEGORY_ID = 7
    settings.MOODLE_STUDENT_ROLE_ID = 5
    settings.MOODLE_EDITING_TEACHER_ROLE_ID = 3
    settings.MOODLE_INSTITUTION = "Student Information System"
    settings.MOODLE_GRADE_SOURCE = "modern_sis"
    stdout = StringIO()

    first_user = create_user(
        username="single-event-user-1",
        email="single-event-user-1@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Single Event User One",
    )
    second_user = create_user(
        username="single-event-user-2",
        email="single-event-user-2@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Single Event User Two",
    )
    target_event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": first_user.id, "action": "UPSERT"},
    )
    untouched_event = IntegrationOutboxEvent.objects.create(
        event_type="USER_SYNC_REQUESTED",
        payload={"user_id": second_user.id, "action": "UPSERT"},
    )

    post_mock = Mock(
        side_effect=[
            Mock(**{"raise_for_status.side_effect": None, "json.return_value": [{"id": 101, "username": first_user.username}]}),
            Mock(**{"raise_for_status.side_effect": None, "json.return_value": {"users": [{"id": 101, "username": first_user.username}]}}),
        ]
    )
    monkeypatch.setattr("requests.post", post_mock)

    call_command("process_moodle_sync", "--event-id", str(target_event.id), stdout=stdout)

    target_event.refresh_from_db()
    untouched_event.refresh_from_db()
    assert target_event.status == IntegrationEventStatus.PROCESSED
    assert untouched_event.status == IntegrationEventStatus.PENDING
    assert "processed=1" in stdout.getvalue()
