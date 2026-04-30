from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from django.conf import settings

from apps.accounts.audit import get_request_ip

from .models import AuditCategory, AuditEvent, AuditSeverity


REDACTED = "[REDACTED]"
JWT_PATTERN = re.compile(r"\b[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\b")
SENSITIVE_KEY_PARTS = (
    "token",
    "password",
    "secret",
    "private_key",
    "private",
    "jwt",
    "authorization",
    "wstoken",
    "access",
    "refresh",
)
SENSITIVE_SETTING_NAMES = (
    "MOODLE_WS_TOKEN",
    "LTI_PRIVATE_KEY",
    "LTI_PUBLIC_KEY",
    "LTI_PLATFORM_PUBLIC_KEY",
    "LTI_PLATFORM_JWKS_JSON",
)


def _is_sensitive_key(key: object) -> bool:
    lowered = str(key).lower().replace("-", "_")
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def _configured_secret_values() -> list[str]:
    values: list[str] = []
    for name in SENSITIVE_SETTING_NAMES:
        value = getattr(settings, name, None)
        if isinstance(value, str) and value.strip():
            values.append(value)
    return values


def sanitize_audit_text(value: Any, *, max_length: int = 1000) -> str:
    text = str(value)
    for secret_value in _configured_secret_values():
        if secret_value:
            text = text.replace(secret_value, REDACTED)
    text = JWT_PATTERN.sub(REDACTED, text)
    if len(text) > max_length:
        return f"{text[: max_length - 1]}..."
    return text


def sanitize_audit_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    if not metadata:
        return {}

    def sanitize_value(key: object, value: Any):
        if _is_sensitive_key(key):
            return REDACTED
        if isinstance(value, Mapping):
            return {str(child_key): sanitize_value(child_key, child_value) for child_key, child_value in value.items()}
        if isinstance(value, str):
            return sanitize_audit_text(value)
        if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
            return [sanitize_value(key, item) for item in value]
        return value

    return {str(key): sanitize_value(key, value) for key, value in metadata.items()}


def record_audit_event(
    *,
    actor=None,
    category: str = AuditCategory.SYSTEM,
    action: str,
    summary: str,
    target_type: str = "",
    target_id: str = "",
    severity: str = AuditSeverity.INFO,
    metadata: Mapping[str, Any] | None = None,
    request=None,
) -> AuditEvent:
    actor_username = ""
    actor_role = ""
    if actor is not None and getattr(actor, "is_authenticated", True):
        actor_username = getattr(actor, "username", "") or ""
        actor_role = getattr(actor, "primary_role", "") or ""

    ip_address = None
    user_agent = ""
    if request is not None:
        ip_address = get_request_ip(request) or None
        user_agent = sanitize_audit_text(request.META.get("HTTP_USER_AGENT", ""), max_length=255)

    return AuditEvent.objects.create(
        actor=actor if getattr(actor, "pk", None) else None,
        actor_username=actor_username,
        actor_role=actor_role,
        category=category,
        action=sanitize_audit_text(action, max_length=80),
        summary=sanitize_audit_text(summary),
        target_type=sanitize_audit_text(target_type, max_length=128),
        target_id=sanitize_audit_text(target_id, max_length=128),
        severity=severity,
        metadata=sanitize_audit_metadata(metadata),
        ip_address=ip_address,
        user_agent=user_agent,
    )


def record_audit_event_safely(**kwargs) -> AuditEvent | None:
    try:
        return record_audit_event(**kwargs)
    except Exception:
        return None
