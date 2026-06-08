from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.repositories import transcripts as transcript_repository

client = TestClient(app)


class DummyUser:
    def __init__(self):
        self.id = "user-123"
        self.email = "user@example.com"
        self.is_active = True
        self.is_admin = False
        self.credit_balance = 0


class DummyTranscript:
    def __init__(self):
        self.id = "transcript-123"
        self.job_id = "job-123"
        self.text = "Das ist ein deutscher Transkripttext."
        self.created_at = datetime(2026, 6, 8, tzinfo=timezone.utc)


class DummyJob:
    def __init__(self):
        self.id = "job-123"
        self.user_id = "user-123"
        self.original_filename = "lecture.mp3"
        self.status = "completed"


class DummyDb:
    pass


async def fake_get_current_user():
    return DummyUser()


async def fake_get_db():
    yield DummyDb()


def test_get_transcript_route_requires_login():
    response = client.get("/api/v1/transcripts/job-123")

    assert response.status_code == 401


def test_get_transcript_route_returns_transcript_for_logged_in_user(monkeypatch):
    async def fake_get_transcript_for_user_by_job_id(db, job_id, user_id):
        assert job_id == "job-123"
        assert user_id == "user-123"
        return DummyTranscript(), DummyJob()

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(
        transcript_repository,
        "get_transcript_for_user_by_job_id",
        fake_get_transcript_for_user_by_job_id,
    )

    response = client.get("/api/v1/transcripts/job-123")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-123"
    assert response.json()["transcript_id"] == "transcript-123"
    assert response.json()["original_filename"] == "lecture.mp3"
    assert response.json()["status"] == "completed"
    assert response.json()["text"] == "Das ist ein deutscher Transkripttext."


def test_get_transcript_route_returns_404_when_missing(monkeypatch):
    async def fake_get_transcript_for_user_by_job_id(db, job_id, user_id):
        return None

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(
        transcript_repository,
        "get_transcript_for_user_by_job_id",
        fake_get_transcript_for_user_by_job_id,
    )

    response = client.get("/api/v1/transcripts/missing-job")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Transcript not found"
