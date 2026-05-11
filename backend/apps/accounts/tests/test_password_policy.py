import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


@pytest.mark.parametrize(
    ("password", "expected_fragment"),
    [
        ("short1!", "at least 10 characters"),
        ("lowercase123!", "uppercase"),
        ("UPPERCASE123!", "lowercase"),
        ("NoDigits!!!!", "digit"),
        ("NoSpecial123", "special"),
    ],
)
def test_validate_password_rejects_non_compliant_passwords(password, expected_fragment):
    with pytest.raises(ValidationError) as exc_info:
        validate_password(password)

    assert any(expected_fragment in message for message in exc_info.value.messages)


def test_validate_password_allows_compliant_password():
    validate_password("SecurePass123!")


def test_create_user_enforces_password_policy(db):
    user_model = get_user_model()

    with pytest.raises(ValidationError):
        user_model.objects.create_user(
            username="weak-user",
            email="weak@example.com",
            password="lowercase123!",
        )
