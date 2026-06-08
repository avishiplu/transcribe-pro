from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript
from app.models.transcription_job import TranscriptionJob
from app.repositories.transcripts import create_transcript
from app.services.file_storage import API_ROOT
from app.services.transcription.groq_provider import transcribe_audio_with_groq


class TranscriptionJobFileMissingError(RuntimeError):
    pass


def resolve_job_audio_path(job: TranscriptionJob) -> Path:
    if not job.stored_file_path:
        raise TranscriptionJobFileMissingError("Transcription job has no stored file path")

    path = Path(job.stored_file_path)

    if path.is_absolute():
        return path

    return API_ROOT / path


async def update_job_status(
    db: AsyncSession,
    job: TranscriptionJob,
    *,
    status: str,
    error_message: str | None = None,
    completed_at: datetime | None = None,
) -> TranscriptionJob:
    job.status = status
    job.error_message = error_message

    if completed_at is not None:
        job.completed_at = completed_at

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return job


async def process_transcription_job(
    db: AsyncSession,
    job: TranscriptionJob,
    *,
    transcribe_func: Callable[..., str] = transcribe_audio_with_groq,
) -> Transcript:
    try:
        await update_job_status(
            db=db,
            job=job,
            status="processing",
        )

        audio_path = resolve_job_audio_path(job)

        transcript_text = transcribe_func(
            file_path=audio_path,
            language_code=job.language_code,
        )

        transcript = await create_transcript(
            db=db,
            job_id=job.id,
            text=transcript_text,
        )

        await update_job_status(
            db=db,
            job=job,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )

        return transcript

    except Exception as error:
        await update_job_status(
            db=db,
            job=job,
            status="failed",
            error_message=str(error),
        )
        raise
