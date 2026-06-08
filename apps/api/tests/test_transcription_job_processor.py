import asyncio
from pathlib import Path

import pytest

from app.models.transcription_job import TranscriptionJob
from app.services.file_storage import API_ROOT
from app.services.transcription.job_processor import (
    TranscriptionJobFileMissingError,
    process_transcription_job,
    resolve_job_audio_path,
)


class DummyAsyncSession:
    def __init__(self):
        self.added_objects = []
        self.commit_count = 0
        self.refreshed_objects = []

    def add(self, obj):
        self.added_objects.append(obj)

    async def commit(self):
        self.commit_count += 1

    async def refresh(self, obj):
        self.refreshed_objects.append(obj)


def make_job(**overrides):
    data = {
        "id": "job-123",
        "user_id": "user-123",
        "original_filename": "lecture.mp3",
        "stored_file_path": "storage/uploads/originals/lecture.mp3",
        "language_code": "en",
        "provider": "groq",
        "status": "queued",
    }
    data.update(overrides)
    return TranscriptionJob(**data)


def test_resolve_job_audio_path_returns_api_relative_path():
    job = make_job(stored_file_path="storage/uploads/originals/lecture.mp3")

    path = resolve_job_audio_path(job)

    assert path == API_ROOT / "storage/uploads/originals/lecture.mp3"


def test_resolve_job_audio_path_rejects_missing_path():
    job = make_job(stored_file_path=None)

    with pytest.raises(TranscriptionJobFileMissingError):
        resolve_job_audio_path(job)


def test_process_transcription_job_creates_transcript_and_marks_completed(tmp_path):
    audio_path = tmp_path / "lecture.mp3"
    audio_path.write_bytes(b"fake audio bytes")

    job = make_job(stored_file_path=str(audio_path))
    db = DummyAsyncSession()

    def fake_transcribe_func(file_path: Path, language_code: str | None = None):
        assert file_path == audio_path
        assert language_code == "en"
        return "This is the transcript text."

    transcript = asyncio.run(
        process_transcription_job(
            db=db,
            job=job,
            transcribe_func=fake_transcribe_func,
        )
    )

    assert transcript.job_id == "job-123"
    assert transcript.text == "This is the transcript text."
    assert job.status == "completed"
    assert job.error_message is None
    assert job.completed_at is not None
    assert db.commit_count == 3


def test_process_transcription_job_marks_failed_when_transcription_fails(tmp_path):
    audio_path = tmp_path / "lecture.mp3"
    audio_path.write_bytes(b"fake audio bytes")

    job = make_job(stored_file_path=str(audio_path))
    db = DummyAsyncSession()

    def fake_transcribe_func(file_path: Path, language_code: str | None = None):
        raise RuntimeError("Groq failed")

    with pytest.raises(RuntimeError):
        asyncio.run(
            process_transcription_job(
                db=db,
                job=job,
                transcribe_func=fake_transcribe_func,
            )
        )

    assert job.status == "failed"
    assert job.error_message == "Groq failed"
