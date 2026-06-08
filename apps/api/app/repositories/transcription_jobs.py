from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcription_job import TranscriptionJob


async def create_transcription_job(
    db: AsyncSession,
    *,
    user_id: str,
    original_filename: str,
    stored_file_path: str | None = None,
    language_code: str | None = None,
    provider: str = "groq",
    status: str = "queued",
    duration_seconds: float | None = None,
) -> TranscriptionJob:
    job = TranscriptionJob(
        id=str(uuid4()),
        user_id=user_id,
        original_filename=original_filename,
        stored_file_path=stored_file_path,
        language_code=language_code,
        provider=provider,
        status=status,
        duration_seconds=duration_seconds,
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return job
