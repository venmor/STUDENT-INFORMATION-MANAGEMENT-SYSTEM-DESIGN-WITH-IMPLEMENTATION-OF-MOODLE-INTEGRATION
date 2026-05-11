from __future__ import annotations

from typing import Any

from .models import AccessLog


def get_request_ip(request) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def record_access_event(
    *,
    event_type: str,
    actor_user=None,
    subject_user=None,
    request=None,
    view_name: str = "",
    status_code: int | None = None,
    metadata: dict[str, Any] | None = None,
):
    request_path = ""
    request_method = ""
    ip_address = ""
    if request is not None:
        request_path = request.path
        request_method = request.method
        ip_address = get_request_ip(request)
        if not view_name:
            resolver_match = getattr(request, "resolver_match", None)
            view_name = getattr(resolver_match, "view_name", "") or ""

    AccessLog.objects.create(
        actor_user=actor_user,
        subject_user=subject_user,
        event_type=event_type,
        view_name=view_name,
        request_path=request_path,
        request_method=request_method,
        response_status=status_code,
        ip_address=ip_address,
        metadata=metadata or {},
    )
