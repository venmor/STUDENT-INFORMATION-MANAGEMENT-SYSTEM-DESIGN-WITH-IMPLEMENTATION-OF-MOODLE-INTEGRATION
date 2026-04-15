from rest_framework.test import APIClient

from apps.accounts.constants import CapabilityName, RoleCode
from apps.accounts.models import UserCapability
from apps.accounts.tests.test_auth_api import create_test_user


def login_client(username: str, password: str) -> APIClient:
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login",
        {"username": username, "password": password},
        format="json",
    )
    assert response.status_code == 200
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access_token']}")
    return client


def test_student_is_denied_from_advisor_probe(db):
    create_test_user(
        username="student1",
        email="student1@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
    )

    client = login_client("student1", "Secret123!")
    response = client.get("/api/v1/auth/probes/advisor")

    assert response.status_code == 403


def test_wellbeing_probe_requires_capability(db):
    create_test_user(
        username="advisor1",
        email="advisor1@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
    )

    client = login_client("advisor1", "Secret123!")
    response = client.get("/api/v1/auth/probes/wellbeing")

    assert response.status_code == 403


def test_wellbeing_probe_denies_students_even_with_capability(db):
    user = create_test_user(
        username="student2",
        email="student2@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
    )
    UserCapability.objects.create(
        user=user,
        capability_name=CapabilityName.WELLBEING_COORDINATOR,
    )

    client = login_client("student2", "Secret123!")
    response = client.get("/api/v1/auth/probes/wellbeing")

    assert response.status_code == 403


def test_wellbeing_probe_allows_staff_with_capability(db):
    user = create_test_user(
        username="advisor2",
        email="advisor2@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
    )
    UserCapability.objects.create(
        user=user,
        capability_name=CapabilityName.WELLBEING_COORDINATOR,
    )

    client = login_client("advisor2", "Secret123!")
    response = client.get("/api/v1/auth/probes/wellbeing")

    assert response.status_code == 200


def test_admin_is_allowed_on_advisor_probe(db):
    create_test_user(
        username="admin2",
        email="admin2@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
    )

    client = login_client("admin2", "Secret123!")
    response = client.get("/api/v1/auth/probes/advisor")

    assert response.status_code == 200
