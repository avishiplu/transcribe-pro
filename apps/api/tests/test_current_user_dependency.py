import asyncio

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from app.dependencies import auth as auth_dependency


class DummyDB:
    pass


class DummyUser:
    def __init__(self, *, id="user-123", is_active=True):
        self.id = id
        self.is_active = is_active


def bearer_credentials(token: str = "valid-token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def test_get_current_user_returns_active_user(monkeypatch):
    async def fake_get_user_by_id(db, user_id):
        return DummyUser(id=user_id, is_active=True)

    monkeypatch.setattr(auth_dependency, "decode_access_token", lambda token: "user-123")
    monkeypatch.setattr(auth_dependency, "get_user_by_id", fake_get_user_by_id)

    user = asyncio.run(
        auth_dependency.get_current_user(
            credentials=bearer_credentials(),
            db=DummyDB(),
        )
    )

    assert user.id == "user-123"


def test_get_current_user_rejects_missing_token():
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_dependency.get_current_user(
                credentials=None,
                db=DummyDB(),
            )
        )

    assert error.value.status_code == 401


def test_get_current_user_rejects_invalid_token(monkeypatch):
    def fake_decode_access_token(token):
        raise JWTError("Invalid token")

    monkeypatch.setattr(auth_dependency, "decode_access_token", fake_decode_access_token)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_dependency.get_current_user(
                credentials=bearer_credentials("bad-token"),
                db=DummyDB(),
            )
        )

    assert error.value.status_code == 401


def test_get_current_user_rejects_missing_user(monkeypatch):
    async def fake_get_user_by_id(db, user_id):
        return None

    monkeypatch.setattr(auth_dependency, "decode_access_token", lambda token: "user-123")
    monkeypatch.setattr(auth_dependency, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_dependency.get_current_user(
                credentials=bearer_credentials(),
                db=DummyDB(),
            )
        )

    assert error.value.status_code == 401


def test_get_current_user_rejects_inactive_user(monkeypatch):
    async def fake_get_user_by_id(db, user_id):
        return DummyUser(id=user_id, is_active=False)

    monkeypatch.setattr(auth_dependency, "decode_access_token", lambda token: "user-123")
    monkeypatch.setattr(auth_dependency, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            auth_dependency.get_current_user(
                credentials=bearer_credentials(),
                db=DummyDB(),
            )
        )

    assert error.value.status_code == 403
