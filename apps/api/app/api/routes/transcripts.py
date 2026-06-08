from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories import transcripts as transcript_repository
from app.schemas.transcript import TranscriptResponse


router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=TranscriptResponse,
)
async def get_transcript(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TranscriptResponse:
    result = await transcript_repository.get_transcript_for_user_by_job_id(
        db=db,
        job_id=job_id,
        user_id=current_user.id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found",
        )

    transcript, job = result

    return TranscriptResponse(
        job_id=job.id,
        transcript_id=transcript.id,
        original_filename=job.original_filename,
        status=job.status,
        text=transcript.text,
        created_at=transcript.created_at,
    )
