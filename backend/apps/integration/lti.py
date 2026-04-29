from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse

import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from jwt.algorithms import RSAAlgorithm

from apps.academics.models import Enrollment
from apps.accounts.constants import RoleCode

from .models import LtiLaunchSession, LtiOidcState, MoodleCourseMap, MoodleUserMap


logger = logging.getLogger(__name__)

LTI_DEPLOYMENT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
LTI_MESSAGE_TYPE_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/message_type"
LTI_VERSION_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/version"
LTI_TARGET_LINK_URI_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/target_link_uri"
LTI_CONTEXT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/context"
LTI_RESOURCE_LINK_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/resource_link"
LTI_ROLES_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/roles"
LTI_LAUNCH_PRESENTATION_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
LTI_CUSTOM_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/custom"

ALLOWED_TOOL_PATHS = {
    "/lti/tools/advising-dashboard": "advising-dashboard",
    "/lti/tools/registration": "registration",
}
ADVISOR_TOOL_ROLES = {RoleCode.ADVISOR, RoleCode.FACULTY, RoleCode.ADMIN}


class LtiError(Exception):
    def __init__(self, message: str, *, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class LtiConfigurationError(LtiError):
    pass


@dataclass(frozen=True)
class LtiLaunchResult:
    session_token: str
    redirect_path: str
    launch_session: LtiLaunchSession


def _read_configured_value(value: str, file_path: str) -> str:
    if value.strip():
        return value.replace("\\n", "\n")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    return ""


def _base64url_uint(value: int) -> str:
    byte_length = (value.bit_length() + 7) // 8
    value_bytes = value.to_bytes(byte_length, byteorder="big")
    return base64.urlsafe_b64encode(value_bytes).rstrip(b"=").decode("ascii")


def pem_public_key_to_jwk(public_key_pem: str, *, kid: str) -> dict[str, str]:
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise LtiConfigurationError("Configured LTI public key is not an RSA public key.", status_code=503)
    numbers = public_key.public_numbers()
    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": _base64url_uint(numbers.n),
        "e": _base64url_uint(numbers.e),
    }


def _tool_public_key_pem() -> str:
    public_key = _read_configured_value(settings.LTI_PUBLIC_KEY, settings.LTI_PUBLIC_KEY_FILE)
    if public_key:
        return public_key

    private_key_pem = _read_configured_value(settings.LTI_PRIVATE_KEY, settings.LTI_PRIVATE_KEY_FILE)
    if not private_key_pem:
        raise LtiConfigurationError("LTI public key is not configured.", status_code=503)
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    public_key = private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


def build_tool_jwks() -> dict[str, list[dict[str, str]]]:
    return {"keys": [pem_public_key_to_jwk(_tool_public_key_pem(), kid=settings.LTI_KEY_ID)]}


def _issuer_allowlist() -> set[str]:
    return set(getattr(settings, "LTI_PLATFORM_ISSUER_ALLOWLIST", []))


def _validate_configured_platform() -> None:
    if not settings.LTI_CLIENT_ID:
        raise LtiConfigurationError("LTI_CLIENT_ID is not configured.", status_code=503)
    if not _issuer_allowlist():
        raise LtiConfigurationError("LTI platform issuer allowlist is not configured.", status_code=503)
    if not settings.LTI_PLATFORM_AUTH_LOGIN_URL:
        raise LtiConfigurationError("LTI_PLATFORM_AUTH_LOGIN_URL is not configured.", status_code=503)


def _safe_tool_path(target_link_uri: str) -> str:
    parsed = urlparse(target_link_uri)
    path = parsed.path
    if path not in ALLOWED_TOOL_PATHS:
        raise LtiError("Unsupported LTI target link URI.", status_code=400)
    return path


def create_oidc_login_redirect(request) -> str:
    _validate_configured_platform()
    query = request.GET
    required = ["iss", "client_id", "login_hint", "target_link_uri"]
    missing = [name for name in required if not query.get(name)]
    if missing:
        raise LtiError(f"Missing required LTI login parameter: {missing[0]}", status_code=400)

    issuer = query["iss"].strip()
    client_id = query["client_id"].strip()
    deployment_id = query.get("lti_deployment_id", "").strip()
    target_link_uri = query["target_link_uri"].strip()
    _safe_tool_path(target_link_uri)

    if issuer not in _issuer_allowlist():
        raise LtiError("LTI platform issuer is not allowed.", status_code=400)
    if client_id != settings.LTI_CLIENT_ID:
        raise LtiError("LTI client_id is not allowed.", status_code=400)
    if deployment_id and settings.LTI_DEPLOYMENT_ID and deployment_id != settings.LTI_DEPLOYMENT_ID:
        raise LtiError("LTI deployment id is not allowed.", status_code=400)

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    LtiOidcState.objects.create(
        state=state,
        nonce=nonce,
        issuer=issuer,
        client_id=client_id,
        deployment_id=deployment_id,
        login_hint=query["login_hint"].strip(),
        lti_message_hint=query.get("lti_message_hint", "").strip(),
        target_link_uri=target_link_uri,
        expires_at=timezone.now() + timedelta(seconds=settings.LTI_STATE_TTL_SECONDS),
    )
    redirect_uri = request.build_absolute_uri(reverse("lti-launch"))
    params = {
        "scope": "openid",
        "response_type": "id_token",
        "response_mode": "form_post",
        "prompt": "none",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "login_hint": query["login_hint"].strip(),
        "state": state,
        "nonce": nonce,
    }
    if query.get("lti_message_hint"):
        params["lti_message_hint"] = query["lti_message_hint"].strip()
    return f"{settings.LTI_PLATFORM_AUTH_LOGIN_URL}?{urlencode(params)}"


def _platform_jwks() -> dict[str, Any]:
    configured_jwks = getattr(settings, "LTI_PLATFORM_JWKS_JSON", None)
    if configured_jwks and configured_jwks.get("keys"):
        return configured_jwks

    platform_public_key = _read_configured_value(
        getattr(settings, "LTI_PLATFORM_PUBLIC_KEY", ""),
        getattr(settings, "LTI_PLATFORM_PUBLIC_KEY_FILE", ""),
    )
    if platform_public_key:
        return {"keys": [pem_public_key_to_jwk(platform_public_key, kid="platform-key")]}

    if settings.LTI_PLATFORM_JWKS_URL:
        try:
            response = requests.get(settings.LTI_PLATFORM_JWKS_URL, timeout=settings.LTI_PLATFORM_JWKS_TIMEOUT)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise LtiConfigurationError("Could not load LTI platform JWKS.", status_code=503) from exc
        if isinstance(payload, dict) and isinstance(payload.get("keys"), list):
            return payload
    raise LtiConfigurationError("LTI platform JWKS is not configured.", status_code=503)


def _platform_key_for_token(id_token: str):
    try:
        header = jwt.get_unverified_header(id_token)
    except jwt.PyJWTError as exc:
        raise LtiError("LTI launch token header is invalid.", status_code=401) from exc
    token_kid = header.get("kid")
    keys = _platform_jwks()["keys"]
    selected_key = None
    if token_kid:
        selected_key = next((key for key in keys if key.get("kid") == token_kid), None)
    if selected_key is None and len(keys) == 1:
        selected_key = keys[0]
    if selected_key is None:
        raise LtiError("No matching LTI platform key was found.", status_code=401)
    return RSAAlgorithm.from_jwk(json.dumps(selected_key))


def _decode_launch_token(id_token: str, state_record: LtiOidcState) -> dict[str, Any]:
    if state_record.issuer not in _issuer_allowlist():
        raise LtiError("LTI platform issuer is not allowed.", status_code=401)
    try:
        return jwt.decode(
            id_token,
            key=_platform_key_for_token(id_token),
            algorithms=["RS256"],
            audience=settings.LTI_CLIENT_ID,
            issuer=state_record.issuer,
            options={"require": ["iss", "aud", "exp", "nonce", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise LtiError("LTI launch token validation failed.", status_code=401) from exc


def _extract_custom_claims(claims: dict[str, Any]) -> dict[str, Any]:
    custom = claims.get(LTI_CUSTOM_CLAIM, {})
    return custom if isinstance(custom, dict) else {}


def _extract_moodle_user_id(claims: dict[str, Any]) -> str:
    custom = _extract_custom_claims(claims)
    for key in ("moodle_user_id", "moodle_userid", "user_id", "userid"):
        value = custom.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    subject = str(claims.get("sub", "")).strip()
    return subject if subject.isdigit() else ""


def _extract_moodle_course_id(claims: dict[str, Any]) -> str:
    custom = _extract_custom_claims(claims)
    for key in ("moodle_course_id", "course_id", "courseid"):
        value = custom.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    context = claims.get(LTI_CONTEXT_CLAIM, {})
    context_id = str(context.get("id", "")).strip() if isinstance(context, dict) else ""
    return context_id if context_id.isdigit() else ""


def _safe_claim_summary(claims: dict[str, Any]) -> dict[str, Any]:
    return {
        "subject": claims.get("sub", ""),
        "name": claims.get("name", ""),
        "email": claims.get("email", ""),
        "target_link_uri": claims.get(LTI_TARGET_LINK_URI_CLAIM, ""),
        "context": claims.get(LTI_CONTEXT_CLAIM, {}),
        "resource_link": claims.get(LTI_RESOURCE_LINK_CLAIM, {}),
        "launch_presentation": claims.get(LTI_LAUNCH_PRESENTATION_CLAIM, {}),
        "custom": _extract_custom_claims(claims),
    }


def _hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode()).hexdigest()


def _resolve_user_map(moodle_user_id: str) -> MoodleUserMap | None:
    if not moodle_user_id.isdigit():
        return None
    return MoodleUserMap.objects.select_related("user").filter(moodle_user_id=int(moodle_user_id)).first()


def _resolve_course_map(moodle_course_id: str) -> MoodleCourseMap | None:
    if not moodle_course_id.isdigit():
        return None
    return MoodleCourseMap.objects.select_related("section__course", "section__faculty_user").filter(
        moodle_course_id=int(moodle_course_id)
    ).first()


def validate_lti_launch(id_token: str, state: str) -> LtiLaunchResult:
    if not id_token or not state:
        raise LtiError("LTI launch is missing id_token or state.", status_code=401)
    try:
        state_record = LtiOidcState.objects.get(state=state)
    except LtiOidcState.DoesNotExist as exc:
        raise LtiError("LTI state was not found or has expired.", status_code=401) from exc

    claims = _decode_launch_token(id_token, state_record)
    target_link_uri = str(claims.get(LTI_TARGET_LINK_URI_CLAIM, ""))
    target_path = _safe_tool_path(target_link_uri)
    expected_path = _safe_tool_path(state_record.target_link_uri)
    if target_path != expected_path:
        raise LtiError("LTI target link URI does not match the login state.", status_code=401)
    if claims.get("nonce") != state_record.nonce:
        raise LtiError("LTI nonce does not match the login state.", status_code=401)
    if claims.get(LTI_MESSAGE_TYPE_CLAIM) != "LtiResourceLinkRequest":
        raise LtiError("Unsupported LTI message type.", status_code=401)
    deployment_id = str(claims.get(LTI_DEPLOYMENT_CLAIM, "")).strip()
    if not deployment_id or deployment_id != settings.LTI_DEPLOYMENT_ID:
        raise LtiError("LTI deployment id is invalid.", status_code=401)

    with transaction.atomic():
        locked_state = LtiOidcState.objects.select_for_update().get(pk=state_record.pk)
        now = timezone.now()
        if locked_state.used_at is not None or locked_state.expires_at <= now:
            raise LtiError("LTI state or nonce has already been used.", status_code=401)
        locked_state.used_at = now
        locked_state.save(update_fields=["used_at"])

    moodle_user_id = _extract_moodle_user_id(claims)
    moodle_course_id = _extract_moodle_course_id(claims)
    user_map = _resolve_user_map(moodle_user_id)
    course_map = _resolve_course_map(moodle_course_id)
    roles = claims.get(LTI_ROLES_CLAIM, [])
    roles = roles if isinstance(roles, list) else []
    session_token = secrets.token_urlsafe(48)
    launch_session = LtiLaunchSession.objects.create(
        session_token_hash=_hash_session_token(session_token),
        issuer=claims["iss"],
        client_id=settings.LTI_CLIENT_ID,
        deployment_id=deployment_id,
        tool_slug=ALLOWED_TOOL_PATHS[target_path],
        moodle_subject=str(claims.get("sub", "")),
        moodle_user_id=moodle_user_id,
        moodle_course_id=moodle_course_id,
        moodle_roles=roles,
        launch_claims=_safe_claim_summary(claims),
        user=user_map.user if user_map else None,
        section=course_map.section if course_map else None,
        expires_at=timezone.now() + timedelta(seconds=settings.LTI_SESSION_TTL_SECONDS),
    )
    return LtiLaunchResult(
        session_token=session_token,
        redirect_path=_redirect_path_for_tool(target_path),
        launch_session=launch_session,
    )


def _redirect_path_for_tool(target_path: str) -> str:
    redirect_base = settings.LTI_LAUNCH_SUCCESS_REDIRECT_BASE
    if not redirect_base:
        return target_path
    return f"{redirect_base}{target_path}"


def build_lti_context(session_token: str, *, requested_tool: str = "") -> dict[str, Any]:
    if not session_token:
        raise LtiError("LTI launch session is required.", status_code=401)
    session_hash = _hash_session_token(session_token)
    launch_session = (
        LtiLaunchSession.objects.select_related("user", "section__course", "section__faculty_user")
        .filter(session_token_hash=session_hash, expires_at__gt=timezone.now())
        .first()
    )
    if launch_session is None:
        raise LtiError("LTI launch session is invalid or expired.", status_code=401)
    if requested_tool and requested_tool != launch_session.tool_slug:
        raise LtiError("LTI launch session does not match this tool.", status_code=403)

    launch_session.last_accessed_at = timezone.now()
    launch_session.save(update_fields=["last_accessed_at"])
    payload = _base_context_payload(launch_session)
    if launch_session.user is None:
        return payload

    if launch_session.tool_slug == "advising-dashboard":
        if launch_session.user.primary_role not in ADVISOR_TOOL_ROLES:
            raise LtiError("This SIS user is not allowed to open the advising LTI tool.", status_code=403)
        if launch_session.section is not None:
            payload["section"] = _section_payload(launch_session.section)
            payload["roster"] = _roster_payload(launch_session.section)
        payload["isMapped"] = launch_session.section is not None
        return payload

    if launch_session.tool_slug == "registration":
        if launch_session.user.primary_role != RoleCode.STUDENT:
            raise LtiError("This SIS user is not allowed to open the registration LTI tool.", status_code=403)
        student_profile = getattr(launch_session.user, "student_profile", None)
        if student_profile is not None:
            payload["student"] = _student_payload(student_profile)
            payload["enrollments"] = _enrollment_payload(student_profile)
            payload["isMapped"] = True
        return payload

    raise LtiError("Unsupported LTI tool.", status_code=404)


def _base_context_payload(launch_session: LtiLaunchSession) -> dict[str, Any]:
    return {
        "tool": launch_session.tool_slug,
        "isMapped": False,
        "launch": {
            "issuer": launch_session.issuer,
            "clientId": launch_session.client_id,
            "deploymentId": launch_session.deployment_id,
            "moodleSubject": launch_session.moodle_subject,
            "moodleUserId": launch_session.moodle_user_id,
            "moodleCourseId": launch_session.moodle_course_id,
            "roles": launch_session.moodle_roles,
            "context": launch_session.launch_claims.get("context", {}),
            "resourceLink": launch_session.launch_claims.get("resource_link", {}),
            "targetLinkUri": launch_session.launch_claims.get("target_link_uri", ""),
        },
        "sisUser": _user_payload(launch_session.user) if launch_session.user else None,
        "section": None,
        "roster": [],
        "student": None,
        "enrollments": [],
    }


def _user_payload(user) -> dict[str, str]:
    return {
        "id": str(user.id),
        "username": user.username,
        "fullName": user.full_name,
        "email": user.email,
        "primaryRole": user.primary_role,
    }


def _section_payload(section) -> dict[str, str | int]:
    return {
        "id": str(section.id),
        "courseCode": section.course.course_code,
        "courseTitle": section.course.course_title,
        "sectionCode": section.section_code,
        "semester": section.semester,
        "academicYear": section.academic_year,
        "faculty": section.faculty_user.full_name or section.faculty_user.username,
        "capacity": section.max_capacity,
    }


def _student_payload(student) -> dict[str, str | int]:
    return {
        "id": str(student.id),
        "studentNumber": student.student_number,
        "fullName": student.user.full_name,
        "email": student.user.email,
        "programme": student.programme,
        "yearOfStudy": student.year_of_study,
        "academicStanding": student.academic_standing,
    }


def _roster_payload(section) -> list[dict[str, str]]:
    enrollments = (
        Enrollment.objects.select_related("student__user")
        .filter(section=section, is_active=True)
        .order_by("student__student_number")
    )
    return [
        {
            "studentId": str(enrollment.student.id),
            "studentNumber": enrollment.student.student_number,
            "fullName": enrollment.student.user.full_name,
            "email": enrollment.student.user.email,
            "enrollmentStatus": enrollment.enrollment_status,
        }
        for enrollment in enrollments
    ]


def _enrollment_payload(student) -> list[dict[str, str]]:
    enrollments = (
        Enrollment.objects.select_related("section__course")
        .filter(student=student, is_active=True)
        .order_by("section__course__course_code", "section__section_code")
    )
    return [
        {
            "enrollmentId": str(enrollment.id),
            "sectionId": str(enrollment.section.id),
            "courseCode": enrollment.section.course.course_code,
            "courseTitle": enrollment.section.course.course_title,
            "sectionCode": enrollment.section.section_code,
            "semester": enrollment.section.semester,
            "academicYear": enrollment.section.academic_year,
            "enrollmentStatus": enrollment.enrollment_status,
        }
        for enrollment in enrollments
    ]
