from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories import transcription_jobs as job_repository
from app.schemas.job import JobStatusResponse


router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobStatusResponse:
    job = await job_repository.get_transcription_job_for_user_by_id(
        db=db,
        job_id=job_id,
        user_id=current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobStatusResponse(
        job_id=job.id,
        original_filename=job.original_filename,
        language_code=job.language_code,
        provider=job.provider,
        status=job.status,
        duration_seconds=job.duration_seconds,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
    )
