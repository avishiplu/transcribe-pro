import asyncio

from app.models.transcription_job import TranscriptionJob
from app.repositories.transcription_jobs import get_transcription_job_for_user_by_id


class DummyResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class DummyAsyncSession:
    def __init__(self, value):
        self.value = value
        self.executed_statement = None

    async def execute(self, statement):
        self.executed_statement = statement
        return DummyResult(self.value)


def test_get_transcription_job_for_user_by_id_returns_job():
    job = TranscriptionJob(
        id="job-123",
        user_id="user-123",
        original_filename="lecture.mp3",
        status="completed",
        provider="groq",
    )
    db = DummyAsyncSession(job)

    result = asyncio.run(
        get_transcription_job_for_user_by_id(
            db=db,
            job_id="job-123",
            user_id="user-123",
        )
    )

    assert result == job
    assert db.executed_statement is not None


def test_get_transcription_job_for_user_by_id_returns_none_when_missing():
    db = DummyAsyncSession(None)

    result = asyncio.run(
        get_transcription_job_for_user_by_id(
            db=db,
            job_id="missing-job",
            user_id="user-123",
        )
    )

    assert result is None
