from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.repositories import transcription_jobs as job_repository

client = TestClient(app)


class DummyUser:
    def __init__(self):
        self.id = "user-123"
        self.email = "user@example.com"
        self.is_active = True
        self.is_admin = False
        self.credit_balance = 0


class DummyJob:
    def __init__(self):
        self.id = "job-123"
        self.user_id = "user-123"
        self.original_filename = "lecture.mp3"
        self.language_code = "de"
        self.provider = "groq"
        self.status = "completed"
        self.duration_seconds = None
        self.error_message = None
        self.created_at = datetime(2026, 6, 8, tzinfo=timezone.utc)
        self.updated_at = datetime(2026, 6, 8, tzinfo=timezone.utc)
        self.completed_at = datetime(2026, 6, 8, tzinfo=timezone.utc)


class DummyDb:
    pass


async def fake_get_current_user():
    return DummyUser()


async def fake_get_db():
    yield DummyDb()


def test_get_job_status_route_requires_login():
    response = client.get("/api/v1/jobs/job-123")

    assert response.status_code == 401


def test_get_job_status_route_returns_job_for_logged_in_user(monkeypatch):
    async def fake_get_transcription_job_for_user_by_id(db, job_id, user_id):
        assert job_id == "job-123"
        assert user_id == "user-123"
        return DummyJob()

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(
        job_repository,
        "get_transcription_job_for_user_by_id",
        fake_get_transcription_job_for_user_by_id,
    )

    response = client.get("/api/v1/jobs/job-123")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == "job-123"
    assert body["original_filename"] == "lecture.mp3"
    assert body["language_code"] == "de"
    assert body["provider"] == "groq"
    assert body["status"] == "completed"
    assert body["error_message"] is None


def test_get_job_status_route_returns_404_when_missing(monkeypatch):
    async def fake_get_transcription_job_for_user_by_id(db, job_id, user_id):
        return None

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(
        job_repository,
        "get_transcription_job_for_user_by_id",
        fake_get_transcription_job_for_user_by_id,
    )

    response = client.get("/api/v1/jobs/missing-job")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
