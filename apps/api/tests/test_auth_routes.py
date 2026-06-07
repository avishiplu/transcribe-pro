from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.schemas.auth import TokenResponse, UserResponse
from app.services import auth as auth_service

client = TestClient(app)


async def fake_get_db():
    yield object()


def test_register_route_returns_user(monkeypatch):
    async def fake_register_user(db, request):
        return UserResponse(
            id="user-123",
            email=request.email,
            is_active=True,
            is_admin=False,
            credit_balance=0,
        )

    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(auth_service, "register_user", fake_register_user)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "safe-password-123",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"
    assert response.json()["credit_balance"] == 0


def test_login_route_returns_token(monkeypatch):
    async def fake_login_user(db, request):
        return TokenResponse(access_token="token-123")

    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(auth_service, "login_user", fake_login_user)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "safe-password-123",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "token-123",
        "token_type": "bearer",
    }
