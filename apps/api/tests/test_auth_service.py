import asyncio

import pytest
from fastapi import HTTPException

from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.services import auth as auth_service


class DummyDB:
    pass


class DummyUser:
    def __init__(
        self,
        *,
        id="user-123",
        email="user@example.com",
        password_hash="hashed-password",
        is_active=True,
        is_admin=False,
        credit_balance=0,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.is_admin = is_admin
        self.credit_balance = credit_balance


def test_register_user_creates_public_user_response(monkeypatch):
    calls = {}

    async def fake_get_user_by_email(db, email):
        calls["lookup_email"] = email
        return None

    async def fake_create_user(db, email, password_hash):
        calls["created_email"] = email
        calls["created_password_hash"] = password_hash
        return DummyUser(email=email, password_hash=password_hash)

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "create_user", fake_create_user)
    monkeypatch.setattr(auth_service, "hash_password", lambda password: "hashed-password")

    response = asyncio.run(
        auth_service.register_user(
            db=DummyDB(),
            request=UserRegisterRequest(
                email="user@example.com",
                password="safe-password-123",
            ),
        )
    )

    assert response.id == "user-123"
    assert response.email == "user@example.com"
    assert response.credit_balance == 0
    assert calls["lookup_email"] == "user@example.com"
    assert calls["created_password_hash"] == "hashed-password"


def test_register_user_rejects_duplicate_email(monkeypatch):
    async def fake_get_user_by_email(db, email):
        return DummyUser(email=email)

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_service.register_user(
                db=DummyDB(),
                request=UserRegisterRequest(
                    email="user@example.com",
                    password="safe-password-123",
                ),
            )
        )

    assert error.value.status_code == 409


def test_login_user_returns_token_for_valid_credentials(monkeypatch):
    async def fake_get_user_by_email(db, email):
        return DummyUser(email=email)

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(auth_service, "create_access_token", lambda subject: f"token-for-{subject}")

    response = asyncio.run(
        auth_service.login_user(
            db=DummyDB(),
            request=UserLoginRequest(
                email="user@example.com",
                password="safe-password-123",
            ),
        )
    )

    assert response.access_token == "token-for-user-123"
    assert response.token_type == "bearer"


def test_login_user_rejects_wrong_password(monkeypatch):
    async def fake_get_user_by_email(db, email):
        return DummyUser(email=email)

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "verify_password", lambda plain, hashed: False)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_service.login_user(
                db=DummyDB(),
                request=UserLoginRequest(
                    email="user@example.com",
                    password="wrong-password",
                ),
            )
        )

    assert error.value.status_code == 401


def test_login_user_rejects_inactive_user(monkeypatch):
    async def fake_get_user_by_email(db, email):
        return DummyUser(email=email, is_active=False)

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_service, "verify_password", lambda plain, hashed: True)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_service.login_user(
                db=DummyDB(),
                request=UserLoginRequest(
                    email="user@example.com",
                    password="safe-password-123",
                ),
            )
        )

    assert error.value.status_code == 403
