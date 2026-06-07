from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from app.main import app

client = TestClient(app)


class DummyUser:
    def __init__(self):
        self.id = "user-123"
        self.email = "user@example.com"
        self.is_active = True
        self.is_admin = False
        self.credit_balance = 0


async def fake_get_current_user():
    return DummyUser()


def test_me_route_returns_current_user():
    app.dependency_overrides[get_current_user] = fake_get_current_user

    response = client.get("/api/v1/auth/me")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": "user-123",
        "email": "user@example.com",
        "is_active": True,
        "is_admin": False,
        "credit_balance": 0,
    }
