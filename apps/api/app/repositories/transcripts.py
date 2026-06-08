from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript


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
