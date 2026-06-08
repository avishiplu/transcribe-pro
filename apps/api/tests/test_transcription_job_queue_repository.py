import asyncio

from app.models.transcription_job import TranscriptionJob
from app.repositories.transcription_jobs import get_next_queued_transcription_job


class DummyResult:
    def __init__(self, job):
        self.job = job

    def scalar_one_or_none(self):
        return self.job


class DummyAsyncSession:
    def __init__(self, job):
        self.job = job
        self.executed_statement = None

    async def execute(self, statement):
        self.executed_statement = statement
        return DummyResult(self.job)


def test_get_next_queued_transcription_job_returns_job():
    job = TranscriptionJob(
        id="job-123",
        user_id="user-123",
        original_filename="lecture.mp3",
        stored_file_path="storage/uploads/originals/lecture.mp3",
        status="queued",
        provider="groq",
    )
    db = DummyAsyncSession(job)

    result = asyncio.run(get_next_queued_transcription_job(db))

    assert result == job
    assert db.executed_statement is not None


def test_get_next_queued_transcription_job_returns_none_when_empty():
    db = DummyAsyncSession(None)

    result = asyncio.run(get_next_queued_transcription_job(db))

    assert result is None
