from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.constants import RoleCode

from .models import Notification, NotificationCategory, NotificationSeverity


SENSITIVE_KEY_PARTS = (
    "token",
    "secret",
    "password",
    "private",
    "key",
    "jwt",
    "authorization",
    "wstoken",
)
REDACTED = "[redacted]"
JWT_PATTERN = re.compile(r"\b[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\b")


def _configured_secret_values() -> list[str]:
    values: list[str] = []
    for setting_name in ("MOODLE_WS_TOKEN", "LTI_PRIVATE_KEY", "LTI_PUBLIC_KEY"):
        value = getattr(settings, setting_name, "")
        if isinstance(value, str) and value:
            values.append(value)
    return values


def sanitize_text(value: object) -> str:
    text = str(value or "")
    for secret in _configured_secret_values():
        text = text.replace(secret, REDACTED)
    text = JWT_PATTERN.sub(REDACTED, text)
    return text


def _is_sensitive_key(key: object) -> bool:
    lowered = str(key).lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def sanitize_metadata(value: Any) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            sanitized[key_text] = REDACTED if _is_sensitive_key(key_text) else sanitize_metadata(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_metadata(item) for item in value[:50]]
    if isinstance(value, tuple):
        return [sanitize_metadata(item) for item in value[:50]]
    if isinstance(value, str):
        return sanitize_text(value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return sanitize_text(value)


def create_notification(
    *,
    recipient,
    category: str,
    severity: str,
    title: str,
    message: str,
    action_label: str = "",
    action_url: str = "",
    source_type: str = "",
    source_id: str = "",
    metadata: dict[str, Any] | None = None,
    is_read: bool = False,
    dedupe: bool = True,
) -> Notification:
    safe_message = sanitize_text(message)[:2000]
    safe_metadata = sanitize_metadata(metadata or {})
    safe_source_id = str(source_id) if source_id else ""

    if dedupe and safe_source_id:
        existing = Notification.objects.filter(
            recipient=recipient,
            category=category,
            severity=severity,
            title=title[:160],
            source_type=source_type[:128],
            source_id=safe_source_id[:128],
            is_read=False,
        ).first()
        if existing:
            return existing

    read_at = timezone.now() if is_read else None
    return Notification.objects.create(
        recipient=recipient,
        category=category,
        severity=severity,
        title=sanitize_text(title)[:160],
        message=safe_message,
        action_label=sanitize_text(action_label)[:80],
        action_url=sanitize_text(action_url)[:255],
        is_read=is_read,
        read_at=read_at,
        source_type=sanitize_text(source_type)[:128],
        source_id=safe_source_id[:128],
        metadata=safe_metadata,
    )


def notify_admins(
    *,
    category: str,
    severity: str,
    title: str,
    message: str,
    action_label: str = "",
    action_url: str = "",
    source_type: str = "",
    source_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> list[Notification]:
    user_model = get_user_model()
    admins = user_model.objects.filter(primary_role=RoleCode.ADMIN, is_active=True)
    return [
        create_notification(
            recipient=admin,
            category=category,
            severity=severity,
            title=title,
            message=message,
            action_label=action_label,
            action_url=action_url,
            source_type=source_type,
            source_id=source_id,
            metadata=metadata,
        )
        for admin in admins
    ]


def notify_moodle_sync_failure(*, event, error: str) -> list[Notification]:
    safe_error = sanitize_text(error)[:500] or "The Moodle sync event failed."
    return notify_admins(
        category=NotificationCategory.MOODLE,
        severity=NotificationSeverity.ERROR,
        title="Moodle sync failed",
        message=f"{event.event_type} failed safely. {safe_error}",
        action_label="Open Moodle Sync",
        action_url="/admin/moodle-sync",
        source_type="IntegrationOutboxEvent",
        source_id=str(event.id),
        metadata={
            "event_type": event.event_type,
            "attempts": event.attempts,
            "status": event.status,
        },
    )
