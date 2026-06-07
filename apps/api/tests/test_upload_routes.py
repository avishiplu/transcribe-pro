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


def test_upload_audio_route_requires_login():
    response = client.post(
        "/api/v1/uploads/audio",
        files={"file": ("lecture.mp3", b"fake audio data", "audio/mpeg")},
    )

    assert response.status_code == 401


def test_upload_audio_route_accepts_audio_file_for_logged_in_user():
    app.dependency_overrides[get_current_user] = fake_get_current_user

    response = client.post(
        "/api/v1/uploads/audio",
        files={"file": ("lecture.mp3", b"fake audio data", "audio/mpeg")},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "lecture.mp3"
    assert body["status"] == "uploaded"
    assert isinstance(body["job_id"], str)
    assert body["job_id"]


def test_upload_audio_route_rejects_unsupported_file_for_logged_in_user():
    app.dependency_overrides[get_current_user] = fake_get_current_user

    response = client.post(
        "/api/v1/uploads/audio",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 400
