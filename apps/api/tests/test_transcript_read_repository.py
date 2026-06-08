import asyncio

from app.models.transcript import Transcript
from app.models.transcription_job import TranscriptionJob
from app.repositories.transcripts import get_transcript_for_user_by_job_id


class DummyResult:
    def __init__(self, value):
        self.value = value

    def first(self):
        return self.value


class DummyAsyncSession:
    def __init__(self, value):
        self.value = value
        self.executed_statement = None

    async def execute(self, statement):
        self.executed_statement = statement
        return DummyResult(self.value)


def test_get_transcript_for_user_by_job_id_returns_transcript_and_job():
    transcript = Transcript(
        id="transcript-123",
        job_id="job-123",
        text="Hallo Welt",
    )
    job = TranscriptionJob(
        id="job-123",
        user_id="user-123",
        original_filename="lecture.mp3",
        status="completed",
        provider="groq",
    )
    db = DummyAsyncSession((transcript, job))

    result = asyncio.run(
        get_transcript_for_user_by_job_id(
            db=db,
            job_id="job-123",
            user_id="user-123",
        )
    )

    assert result == (transcript, job)
    assert db.executed_statement is not None


def test_get_transcript_for_user_by_job_id_returns_none_when_missing():
    db = DummyAsyncSession(None)

    result = asyncio.run(
        get_transcript_for_user_by_job_id(
            db=db,
            job_id="missing-job",
            user_id="user-123",
        )
    )

    assert result is None
