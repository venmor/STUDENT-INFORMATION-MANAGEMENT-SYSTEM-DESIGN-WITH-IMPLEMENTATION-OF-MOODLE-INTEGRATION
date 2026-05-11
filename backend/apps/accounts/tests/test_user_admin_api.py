from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.testutils import authenticate_client, create_user


def test_admin_can_create_user_with_temporary_password(db):
    admin_user = create_user(
        username="admin-step23",
        email="admin-step23@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="System Admin",
    )
    client = authenticate_client(username=admin_user.username, password="Secret123!")

    response = client.post(
        "/api/v1/users",
        {
            "username": "student-temp",
            "email": "student-temp@example.com",
            "full_name": "Student Temp",
            "primary_role": RoleCode.STUDENT,
            "temporary_password": "TempPass123!",
        },
        format="json",
    )

    assert response.status_code == 201, response.json()
    body = response.json()
    assert body["must_reset_password"] is True
    assert body["primary_role"] == RoleCode.STUDENT


def test_admin_user_creation_rejects_weak_temporary_password(db):
    admin_user = create_user(
        username="admin-weak-create",
        email="admin-weak-create@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="System Admin",
    )
    client = authenticate_client(username=admin_user.username, password="Secret123!")

    response = client.post(
        "/api/v1/users",
        {
            "username": "weak-temp",
            "email": "weak-temp@example.com",
            "full_name": "Weak Temp",
            "primary_role": RoleCode.STUDENT,
            "temporary_password": "weakpass123!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "temporary_password" in response.json()


def test_change_password_requires_current_password_and_updates_credentials(db):
    user = create_user(
        username="password-owner",
        email="password-owner@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Password Owner",
    )
    client = authenticate_client(username=user.username, password="Secret123!")

    response = client.post(
        "/api/v1/users/change-password",
        {
            "current_password": "Secret123!",
            "new_password": "Stronger123!",
        },
        format="json",
    )

    assert response.status_code == 200, response.json()

    old_login = APIClient().post(
        "/api/v1/auth/login",
        {"username": user.username, "password": "Secret123!"},
        format="json",
    )
    new_login = APIClient().post(
        "/api/v1/auth/login",
        {"username": user.username, "password": "Stronger123!"},
        format="json",
    )

    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_admin_reset_password_requires_policy_and_sets_reset_flag(db):
    user_model = get_user_model()
    admin_user = create_user(
        username="admin-reset",
        email="admin-reset@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="System Admin",
    )
    target_user = create_user(
        username="reset-target",
        email="reset-target@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Reset Target",
    )
    client = authenticate_client(username=admin_user.username, password="Secret123!")

    weak_response = client.post(
        f"/api/v1/users/{target_user.id}/reset-password",
        {"new_password": "weakpass123!"},
        format="json",
    )
    assert weak_response.status_code == 400

    response = client.post(
        f"/api/v1/users/{target_user.id}/reset-password",
        {"new_password": "ResetPass123!"},
        format="json",
    )

    assert response.status_code == 200, response.json()

    refreshed_user = user_model.objects.get(pk=target_user.pk)
    assert refreshed_user.must_reset_password is True


def test_deactivated_account_cannot_log_in(db):
    admin_user = create_user(
        username="admin-deactivate",
        email="admin-deactivate@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="System Admin",
    )
    target_user = create_user(
        username="deactivate-me",
        email="deactivate-me@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Deactivate Me",
    )
    client = authenticate_client(username=admin_user.username, password="Secret123!")

    response = client.post(f"/api/v1/users/{target_user.id}/deactivate", format="json")

    assert response.status_code == 200, response.json()

    login_response = APIClient().post(
        "/api/v1/auth/login",
        {"username": target_user.username, "password": "Secret123!"},
        format="json",
    )
    assert login_response.status_code == 401


def test_admin_can_view_access_logs_for_user(db):
    admin_user = create_user(
        username="admin-audit",
        email="admin-audit@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="System Admin",
    )
    target_user = create_user(
        username="audit-target",
        email="audit-target@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Audit Target",
    )
    APIClient().post(
        "/api/v1/auth/login",
        {"username": target_user.username, "password": "wrong-password"},
        format="json",
    )
    APIClient().post(
        "/api/v1/auth/login",
        {"username": target_user.username, "password": "Secret123!"},
        format="json",
    )

    client = authenticate_client(username=admin_user.username, password="Secret123!")
    response = client.get(f"/api/v1/users/{target_user.id}/access-logs")

    assert response.status_code == 200, response.json()
    assert len(response.json()) >= 2

