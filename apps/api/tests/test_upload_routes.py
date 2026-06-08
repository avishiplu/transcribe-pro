from fastapi.testclient import TestClient

from app.db.session import get_db
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


class FakeDb:
    def __init__(self):
        self.added_objects = []
        self.committed = False
        self.refreshed_objects = []

    def add(self, obj):
        self.added_objects.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed_objects.append(obj)


async def fake_get_current_user():
    return DummyUser()


def test_upload_audio_route_requires_login():
    response = client.post(
        "/api/v1/uploads/audio",
        files={"file": ("lecture.mp3", b"fake audio data", "audio/mpeg")},
    )

    assert response.status_code == 401


def test_upload_audio_route_creates_transcription_job_for_logged_in_user():
    fake_db = FakeDb()

    async def fake_get_db():
        yield fake_db

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_db] = fake_get_db

    response = client.post(
        "/api/v1/uploads/audio",
        files={"file": ("lecture.mp3", b"fake audio data", "audio/mpeg")},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()

    assert body["filename"] == "lecture.mp3"
    assert body["status"] == "queued"
    assert isinstance(body["job_id"], str)
    assert body["job_id"]

    assert len(fake_db.added_objects) == 1
    created_job = fake_db.added_objects[0]
    assert created_job.user_id == "user-123"
    assert created_job.original_filename == "lecture.mp3"
    assert created_job.status == "queued"
    assert created_job.provider == "groq"

    assert fake_db.committed is True
    assert fake_db.refreshed_objects == [created_job]


def test_upload_audio_route_rejects_unsupported_file_for_logged_in_user():
    fake_db = FakeDb()

    async def fake_get_db():
        yield fake_db

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_db] = fake_get_db

    response = client.post(
        "/api/v1/uploads/audio",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert fake_db.added_objects == []
    assert fake_db.committed is False
