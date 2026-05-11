from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.utils import timezone
from rest_framework.test import APIClient

from apps.academics.models import (
    Course,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentStatus,
)
from apps.accounts.constants import RoleCode
from apps.integration.models import (
    LtiLaunchSession,
    LtiOidcState,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.students.models import StudentProfile
from apps.testutils import create_user


LTI_DEPLOYMENT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/deployment_id"
LTI_MESSAGE_TYPE_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/message_type"
LTI_VERSION_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/version"
LTI_TARGET_LINK_URI_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/target_link_uri"
LTI_CONTEXT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/context"
LTI_RESOURCE_LINK_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/resource_link"
LTI_ROLES_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/roles"
LTI_LAUNCH_PRESENTATION_CLAIM = (
    "https://purl.imsglobal.org/spec/lti/claim/launch_presentation"
)
LTI_CUSTOM_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/custom"


@pytest.fixture()
def rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


@pytest.fixture()
def platform_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


@pytest.fixture()
def lti_settings(settings, rsa_key_pair, platform_key_pair):
    from apps.integration.lti import pem_public_key_to_jwk

    tool_private_key, tool_public_key = rsa_key_pair
    platform_private_key, platform_public_key = platform_key_pair
    settings.LTI_PRIVATE_KEY = tool_private_key
    settings.LTI_PUBLIC_KEY = tool_public_key
    settings.LTI_KEY_ID = "sis-lti-key"
    settings.LTI_PLATFORM_ISSUER_ALLOWLIST = ["https://moodle.example.test"]
    settings.LTI_CLIENT_ID = "client-123"
    settings.LTI_DEPLOYMENT_ID = "deployment-456"
    settings.LTI_PLATFORM_AUTH_LOGIN_URL = (
        "https://moodle.example.test/mod/lti/auth.php"
    )
    settings.LTI_PLATFORM_JWKS_JSON = {
        "keys": [pem_public_key_to_jwk(platform_public_key, kid="moodle-key")]
    }
    settings.LTI_LAUNCH_SUCCESS_REDIRECT_BASE = ""
    settings.LTI_STATE_TTL_SECONDS = 600
    settings.LTI_SESSION_TTL_SECONDS = 3600
    settings.LTI_SESSION_COOKIE_NAME = "sis_lti_session"
    settings.LTI_SESSION_COOKIE_SECURE = False
    settings.LTI_SESSION_COOKIE_SAMESITE = "Lax"
    return {
        "tool_private_key": tool_private_key,
        "tool_public_key": tool_public_key,
        "platform_private_key": platform_private_key,
        "platform_public_key": platform_public_key,
    }


def create_lti_state(
    *, target_link_uri: str = "http://testserver/lti/tools/advising-dashboard"
):
    return LtiOidcState.objects.create(
        state="state-123",
        nonce="nonce-123",
        issuer="https://moodle.example.test",
        client_id="client-123",
        deployment_id="deployment-456",
        login_hint="login-hint",
        lti_message_hint="message-hint",
        target_link_uri=target_link_uri,
        expires_at=timezone.now() + timedelta(minutes=10),
    )


def create_id_token(
    private_key: str,
    *,
    overrides: dict | None = None,
    target_link_uri: str | None = None,
) -> str:
    now = timezone.now()
    claims = {
        "iss": "https://moodle.example.test",
        "aud": "client-123",
        "sub": "moodle-sub-42",
        "exp": int((now + timedelta(minutes=5)).timestamp()),
        "iat": int(now.timestamp()),
        "nonce": "nonce-123",
        "name": "Moodle User",
        "email": "moodle-user@example.test",
        LTI_DEPLOYMENT_CLAIM: "deployment-456",
        LTI_MESSAGE_TYPE_CLAIM: "LtiResourceLinkRequest",
        LTI_VERSION_CLAIM: "1.3.0",
        LTI_TARGET_LINK_URI_CLAIM: target_link_uri
        or "http://testserver/lti/tools/advising-dashboard",
        LTI_CONTEXT_CLAIM: {"id": "77", "label": "CSC101", "title": "Intro CS"},
        LTI_RESOURCE_LINK_CLAIM: {"id": "resource-1", "title": "SIS Tool"},
        LTI_ROLES_CLAIM: [
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"
        ],
        LTI_LAUNCH_PRESENTATION_CLAIM: {"document_target": "iframe"},
        LTI_CUSTOM_CLAIM: {"moodle_user_id": "42", "moodle_course_id": "77"},
    }
    if overrides:
        for key, value in overrides.items():
            if value is None:
                claims.pop(key, None)
            else:
                claims[key] = value
    return jwt.encode(
        claims, private_key, algorithm="RS256", headers={"kid": "moodle-key"}
    )


def create_section(*, faculty_user=None):
    faculty = faculty_user or create_user(
        username="faculty-lti",
        email="faculty-lti@example.com",
        primary_role=RoleCode.FACULTY,
        full_name="Faculty LTI",
    )
    course = Course.objects.create(
        course_code="CSC101",
        course_title="Intro CS",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=40,
        is_active=True,
    )
    now = timezone.now()
    section = CourseSection.objects.create(
        course=course,
        section_code="A1",
        faculty_user=faculty,
        room="LT-1",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=40,
        registration_opens_at=now - timedelta(days=7),
        registration_closes_at=now + timedelta(days=7),
        drop_deadline=now + timedelta(days=14),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    return section


def create_student_profile(
    *, username: str = "student-lti", student_number: str = "2026/CS/001"
):
    user = create_user(
        username=username,
        email=f"{username}@example.com",
        primary_role=RoleCode.STUDENT,
        full_name="Student LTI",
    )
    student = StudentProfile.objects.create(
        user=user,
        student_number=student_number,
        national_id=f"NRC-{student_number}",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=2,
    )
    return user, student


@pytest.mark.django_db
def test_jwks_returns_public_key_without_private_material(lti_settings):
    response = APIClient().get("/lti/jwks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["keys"][0]["kid"] == "sis-lti-key"
    assert payload["keys"][0]["kty"] == "RSA"
    assert "n" in payload["keys"][0]
    assert "e" in payload["keys"][0]
    serialized = json.dumps(payload)
    assert "PRIVATE KEY" not in serialized
    assert '"d"' not in serialized
    assert '"p"' not in serialized
    assert '"q"' not in serialized


@pytest.mark.django_db
def test_oidc_login_rejects_missing_required_parameters(lti_settings):
    response = APIClient().get("/lti/login", {"iss": "https://moodle.example.test"})

    assert response.status_code == 400
    body = response.content.decode()
    assert "Missing required LTI login parameter" in body
    assert "PRIVATE KEY" not in body


@pytest.mark.django_db
def test_oidc_login_creates_state_and_redirects_to_platform_authorization(lti_settings):
    response = APIClient().get(
        "/lti/login",
        {
            "iss": "https://moodle.example.test",
            "client_id": "client-123",
            "login_hint": "login-hint",
            "lti_message_hint": "message-hint",
            "target_link_uri": "http://testserver/lti/tools/advising-dashboard",
            "lti_deployment_id": "deployment-456",
        },
    )

    assert response.status_code == 302
    location = response["Location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    assert (
        f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        == "https://moodle.example.test/mod/lti/auth.php"
    )
    assert query["scope"] == ["openid"]
    assert query["response_type"] == ["id_token"]
    assert query["response_mode"] == ["form_post"]
    assert query["prompt"] == ["none"]
    assert query["client_id"] == ["client-123"]
    assert query["login_hint"] == ["login-hint"]
    assert query["lti_message_hint"] == ["message-hint"]
    assert query["redirect_uri"] == ["http://testserver/lti/launch"]
    stored_state = LtiOidcState.objects.get(state=query["state"][0])
    assert stored_state.nonce == query["nonce"][0]
    assert stored_state.used_at is None


@pytest.mark.django_db
def test_launch_accepts_valid_id_token_and_sets_lti_session_cookie(lti_settings):
    create_lti_state()
    token = create_id_token(lti_settings["platform_private_key"])

    response = APIClient().post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    assert response.status_code == 302
    assert response["Location"] == "/lti/tools/advising-dashboard"
    assert "sis_lti_session" in response.cookies
    launch_session = LtiLaunchSession.objects.get()
    assert launch_session.issuer == "https://moodle.example.test"
    assert launch_session.client_id == "client-123"
    assert launch_session.deployment_id == "deployment-456"
    assert launch_session.tool_slug == "advising-dashboard"
    assert launch_session.moodle_user_id == "42"
    assert launch_session.moodle_course_id == "77"
    assert launch_session.session_token_hash
    assert token not in json.dumps(launch_session.launch_claims)


@pytest.mark.django_db
def test_launch_rejects_invalid_issuer_without_creating_session(lti_settings):
    create_lti_state()
    token = create_id_token(
        lti_settings["platform_private_key"],
        overrides={"iss": "https://evil.example.test"},
    )

    response = APIClient().post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    assert response.status_code == 401
    assert LtiLaunchSession.objects.count() == 0


@pytest.mark.django_db
def test_launch_rejects_invalid_audience(lti_settings):
    create_lti_state()
    token = create_id_token(
        lti_settings["platform_private_key"], overrides={"aud": "wrong-client"}
    )

    response = APIClient().post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    assert response.status_code == 401
    assert b"wrong-client" not in response.content


@pytest.mark.django_db
def test_launch_rejects_expired_token(lti_settings):
    create_lti_state()
    token = create_id_token(
        lti_settings["platform_private_key"],
        overrides={"exp": int((timezone.now() - timedelta(minutes=1)).timestamp())},
    )

    response = APIClient().post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_launch_rejects_missing_deployment_id(lti_settings):
    create_lti_state()
    token = create_id_token(
        lti_settings["platform_private_key"], overrides={LTI_DEPLOYMENT_CLAIM: None}
    )

    response = APIClient().post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_launch_rejects_missing_state(lti_settings):
    token = create_id_token(lti_settings["platform_private_key"])

    response = APIClient().post("/lti/launch", {"id_token": token})

    assert response.status_code == 401


@pytest.mark.django_db
def test_launch_rejects_replayed_state_and_nonce(lti_settings):
    create_lti_state()
    token = create_id_token(lti_settings["platform_private_key"])
    client = APIClient()

    first_response = client.post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )
    second_response = client.post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 401
    assert LtiLaunchSession.objects.count() == 1


@pytest.mark.django_db
def test_context_api_denies_access_without_valid_lti_session(lti_settings):
    response = APIClient().get("/lti/api/session", {"tool": "advising-dashboard"})

    assert response.status_code == 401


@pytest.mark.django_db
def test_context_api_returns_limited_unmapped_context(lti_settings):
    create_lti_state()
    token = create_id_token(lti_settings["platform_private_key"])
    client = APIClient()
    launch_response = client.post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    response = client.get("/lti/api/session", {"tool": "advising-dashboard"})

    assert launch_response.status_code == 302
    assert response.status_code == 200
    payload = response.json()
    assert payload["tool"] == "advising-dashboard"
    assert payload["isMapped"] is False
    assert payload["sisUser"] is None
    assert payload["section"] is None
    assert payload["roster"] == []
    assert payload["launch"]["moodleUserId"] == "42"


@pytest.mark.django_db
def test_context_api_returns_mapped_advising_context_with_roster(lti_settings):
    advisor = create_user(
        username="advisor-lti",
        email="advisor-lti@example.com",
        primary_role=RoleCode.ADVISOR,
        full_name="Advisor LTI",
    )
    section = create_section()
    student_user, student = create_student_profile()
    MoodleUserMap.objects.create(
        user=advisor, moodle_user_id=42, moodle_username="advisor-lti"
    )
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=77,
        moodle_shortname="CSC101-A1-2026_2027-SEM1",
        moodle_category_id=1,
    )
    Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=EnrollmentStatus.ENROLLED,
        actor_role=RoleCode.ADMIN,
        actor_user=advisor,
        is_active=True,
    )
    run = MoodleEngagementIngestionRun.objects.create(
        status=MoodleEngagementIngestionStatus.SUCCEEDED,
        courses_inspected=1,
        users_inspected=1,
        snapshots_created=1,
        completed_at=timezone.now(),
    )
    collected_at = timezone.now()
    MoodleEngagementSnapshot.objects.create(
        run=run,
        user=student_user,
        student=student,
        section=section,
        moodle_user_id=5501,
        moodle_course_id=77,
        moodle_last_access_at=collected_at - timedelta(hours=2),
        moodle_course_last_access_at=collected_at - timedelta(hours=1),
        collected_at=collected_at,
    )
    create_lti_state()
    token = create_id_token(lti_settings["platform_private_key"])
    client = APIClient()
    client.post("/lti/launch", {"id_token": token, "state": "state-123"})

    response = client.get("/lti/api/session", {"tool": "advising-dashboard"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["isMapped"] is True
    assert payload["sisUser"]["username"] == "advisor-lti"
    assert payload["sisUser"]["primaryRole"] == RoleCode.ADVISOR
    assert payload["section"]["courseCode"] == "CSC101"
    assert payload["roster"] == [
        {
            "studentId": str(student.id),
            "studentNumber": student.student_number,
            "fullName": student_user.full_name,
            "email": student_user.email,
            "enrollmentStatus": EnrollmentStatus.ENROLLED,
            "engagement": {
                "collectedAt": collected_at.isoformat().replace("+00:00", "Z"),
                "moodleLastAccessAt": (collected_at - timedelta(hours=2))
                .isoformat()
                .replace("+00:00", "Z"),
                "moodleCourseLastAccessAt": (collected_at - timedelta(hours=1))
                .isoformat()
                .replace("+00:00", "Z"),
                "assignmentSubmissionCount": None,
                "assignmentSubmissionRate": None,
                "quizAttemptCount": None,
                "quizAverage": None,
                "forumPostCount": None,
            },
        }
    ]


@pytest.mark.django_db
def test_context_api_returns_mapped_registration_context_for_student(lti_settings):
    target_link_uri = "http://testserver/lti/tools/registration"
    student_user, student = create_student_profile(
        username="registration-lti", student_number="2026/CS/002"
    )
    section = create_section()
    MoodleUserMap.objects.create(
        user=student_user, moodle_user_id=42, moodle_username="registration-lti"
    )
    MoodleCourseMap.objects.create(
        section=section,
        moodle_course_id=77,
        moodle_shortname="CSC101-A1-2026_2027-SEM1",
        moodle_category_id=1,
    )
    Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=EnrollmentStatus.ENROLLED,
        actor_role=RoleCode.STUDENT,
        actor_user=student_user,
        is_active=True,
    )
    create_lti_state(target_link_uri=target_link_uri)
    token = create_id_token(
        lti_settings["platform_private_key"], target_link_uri=target_link_uri
    )
    client = APIClient()
    client.post("/lti/launch", {"id_token": token, "state": "state-123"})

    response = client.get("/lti/api/session", {"tool": "registration"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["tool"] == "registration"
    assert payload["sisUser"]["username"] == "registration-lti"
    assert payload["student"]["studentNumber"] == "2026/CS/002"
    assert payload["enrollments"][0]["courseCode"] == "CSC101"


@pytest.mark.django_db
def test_lti_errors_do_not_leak_tokens_or_private_key_material(lti_settings):
    create_lti_state()
    token = create_id_token(
        lti_settings["platform_private_key"], overrides={"aud": "wrong-client"}
    )

    response = APIClient().post(
        "/lti/launch", {"id_token": token, "state": "state-123"}
    )

    body = response.content.decode()
    assert response.status_code == 401
    assert token not in body
    assert "PRIVATE KEY" not in body
