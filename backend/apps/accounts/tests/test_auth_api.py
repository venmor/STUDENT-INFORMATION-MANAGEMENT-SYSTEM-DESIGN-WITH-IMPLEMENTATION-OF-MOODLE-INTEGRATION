from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


def create_test_user(**overrides):
    user_model = get_user_model()
    field_names = {field.name for field in user_model._meta.get_fields()}
    create_kwargs = {
        "username": overrides.pop("username", "admin1"),
        "email": overrides.pop("email", "admin@example.com"),
        "password": overrides.pop("password", "Secret123!"),
    }
    if "primary_role" in field_names:
        create_kwargs["primary_role"] = overrides.pop("primary_role", "ADMIN")
    create_kwargs.update(overrides)
    return user_model.objects.create_user(**create_kwargs)


def test_login_returns_token_pair(db):
    create_test_user()

    client = APIClient()
    response = client.post(
        "/api/v1/auth/login",
        {"username": "admin1", "password": "Secret123!"},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["expires_in"] == 900


def test_login_rejects_wrong_password(db):
    create_test_user()

    client = APIClient()
    response = client.post(
        "/api/v1/auth/login",
        {"username": "admin1", "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == 401


def test_refresh_returns_new_access_token(db):
    create_test_user()

    client = APIClient()
    login_response = client.post(
        "/api/v1/auth/login",
        {"username": "admin1", "password": "Secret123!"},
        format="json",
    )
    assert login_response.status_code == 200

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        {"refresh_token": login_response.json()["refresh_token"]},
        format="json",
    )

    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["expires_in"] == 900


def test_passwords_are_hashed_with_bcrypt_sha256_and_minimum_rounds(db):
    user = create_test_user()

    hasher = identify_hasher(user.password)

    assert hasher.algorithm == "bcrypt_sha256"
    assert getattr(hasher, "rounds", 0) >= 12
