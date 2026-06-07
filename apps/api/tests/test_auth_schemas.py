import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


def test_register_request_accepts_valid_data():
    data = UserRegisterRequest(
        email="user@example.com",
        password="safe-password-123",
    )

    assert data.email == "user@example.com"
    assert data.password == "safe-password-123"


def test_register_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="not-an-email",
            password="safe-password-123",
        )


def test_register_request_rejects_short_password():
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="user@example.com",
            password="short",
        )


def test_token_response_defaults_to_bearer():
    token = TokenResponse(access_token="abc123")

    assert token.access_token == "abc123"
    assert token.token_type == "bearer"


def test_user_response_accepts_public_user_data():
    user = UserResponse(
        id="user-123",
        email="user@example.com",
        is_active=True,
        is_admin=False,
        credit_balance=0,
    )

    assert user.id == "user-123"
    assert user.credit_balance == 0
