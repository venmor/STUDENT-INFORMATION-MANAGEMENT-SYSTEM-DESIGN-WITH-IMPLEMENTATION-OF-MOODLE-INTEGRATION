from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode


def create_user(**overrides):
    user_model = get_user_model()
    create_kwargs = {
        "username": overrides.pop("username", "user1"),
        "email": overrides.pop("email", "user1@example.com"),
        "password": overrides.pop("password", "Secret123!"),
        "primary_role": overrides.pop("primary_role", RoleCode.STUDENT),
        "full_name": overrides.pop("full_name", "Test User"),
    }
    create_kwargs.update(overrides)
    return user_model.objects.create_user(**create_kwargs)


def authenticate_client(*, username: str, password: str) -> APIClient:
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login",
        {"username": username, "password": password},
        format="json",
    )
    assert response.status_code == 200, response.json()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access_token']}")
    return client


def authenticated_client_for_user(user, password: str = "Secret123!") -> APIClient:
    return authenticate_client(username=user.username, password=password)
