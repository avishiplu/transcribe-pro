import asyncio

from app.models.transcript import Transcript
from app.repositories.transcripts import build_transcript_for_create, create_transcript


class DummyAsyncSession:
    def __init__(self):
        self.added_object = None
        self.committed = False
        self.refreshed_object = None

    def add(self, obj):
        self.added_object = obj

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed_object = obj


def test_build_transcript_for_create_returns_transcript_model():
    transcript = build_transcript_for_create(
        job_id="job-123",
        text="Hello transcript",
        export_file_path="exports/job-123.txt",
    )

    assert isinstance(transcript, Transcript)
    assert transcript.id
    assert transcript.job_id == "job-123"
    assert transcript.text == "Hello transcript"
    assert transcript.export_file_path == "exports/job-123.txt"


def test_create_transcript_adds_commits_and_refreshes_transcript():
    db = DummyAsyncSession()

    transcript = asyncio.run(
        create_transcript(
            db=db,
            job_id="job-123",
            text="Hello transcript",
        )
    )

    assert db.added_object == transcript
    assert db.committed is True
    assert db.refreshed_object == transcript
    assert transcript.job_id == "job-123"
    assert transcript.text == "Hello transcript"
