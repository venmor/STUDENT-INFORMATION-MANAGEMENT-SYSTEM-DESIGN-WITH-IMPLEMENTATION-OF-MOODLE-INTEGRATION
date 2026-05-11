from __future__ import annotations

import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .lti import LtiError, build_lti_context, build_tool_jwks, create_oidc_login_redirect, validate_lti_launch


logger = logging.getLogger(__name__)


def _safe_error_response(message: str, *, status: int):
    return JsonResponse({"error": {"code": "lti_error", "message": message}}, status=status)


@require_GET
def jwks(request):
    try:
        return JsonResponse(build_tool_jwks())
    except LtiError as exc:
        logger.warning("LTI JWKS configuration failure: %s", exc)
        return _safe_error_response(str(exc), status=exc.status_code)


@require_GET
def login(request):
    try:
        return redirect(create_oidc_login_redirect(request))
    except LtiError as exc:
        logger.warning("LTI OIDC login rejected: %s", exc)
        return _safe_error_response(str(exc), status=exc.status_code)


@csrf_exempt
@require_POST
def launch(request):
    try:
        launch_result = validate_lti_launch(
            request.POST.get("id_token", ""),
            request.POST.get("state", ""),
        )
    except LtiError as exc:
        logger.warning("LTI launch rejected: %s", exc)
        return _safe_error_response("LTI launch validation failed.", status=exc.status_code)

    response = redirect(launch_result.redirect_path)
    response.set_cookie(
        settings.LTI_SESSION_COOKIE_NAME,
        launch_result.session_token,
        max_age=settings.LTI_SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.LTI_SESSION_COOKIE_SECURE,
        samesite=settings.LTI_SESSION_COOKIE_SAMESITE,
    )
    return response


@require_GET
def session_context(request):
    try:
        payload = build_lti_context(
            request.COOKIES.get(settings.LTI_SESSION_COOKIE_NAME, ""),
            requested_tool=request.GET.get("tool", ""),
        )
    except LtiError as exc:
        return _safe_error_response(str(exc), status=exc.status_code)
    return JsonResponse(payload)
