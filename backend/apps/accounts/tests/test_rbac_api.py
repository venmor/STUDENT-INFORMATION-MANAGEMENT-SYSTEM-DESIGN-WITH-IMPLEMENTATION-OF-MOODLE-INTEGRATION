from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
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
