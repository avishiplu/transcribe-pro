from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript
from app.models.transcription_job import TranscriptionJob


def build_transcript_for_create(
    *,
    job_id: str,
    text: str,
    export_file_path: str | None = None,
) -> Transcript:
    return Transcript(
        id=str(uuid4()),
        job_id=job_id,
        text=text,
        export_file_path=export_file_path,
    )


async def create_transcript(
    db: AsyncSession,
    *,
    job_id: str,
    text: str,
    export_file_path: str | None = None,
) -> Transcript:
    transcript = build_transcript_for_create(
        job_id=job_id,
        text=text,
        export_file_path=export_file_path,
    )

    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)

    return transcript


async def get_transcript_for_user_by_job_id(
    db: AsyncSession,
    *,
    job_id: str,
    user_id: str,
) -> tuple[Transcript, TranscriptionJob] | None:
    result = await db.execute(
        select(Transcript, TranscriptionJob)
        .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
        .where(Transcript.job_id == job_id)
        .where(TranscriptionJob.user_id == user_id)
    )

    return result.first()
