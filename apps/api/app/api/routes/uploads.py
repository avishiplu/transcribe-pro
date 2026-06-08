from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.transcription_jobs import create_transcription_job
from app.schemas.upload import UploadAcceptedResponse
from app.services.file_storage import save_uploaded_audio_file
from app.services.upload_validation import validate_upload_metadata


router = APIRouter()


@router.post(
    "/audio",
    response_model=UploadAcceptedResponse,
)
async def upload_audio(
    file: UploadFile = File(...),
    language_code: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadAcceptedResponse:
    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)

    upload_metadata = validate_upload_metadata(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
    )

    normalized_language_code = language_code.strip().lower() if language_code else None

    stored_file_path = save_uploaded_audio_file(
        file=file,
        extension=upload_metadata.extension,
    )

    job = await create_transcription_job(
        db,
        user_id=current_user.id,
        original_filename=upload_metadata.filename,
        stored_file_path=stored_file_path,
        language_code=normalized_language_code,
        provider="groq",
        status="queued",
        duration_seconds=None,
    )

    return UploadAcceptedResponse(
        job_id=job.id,
        filename=job.original_filename,
        status=job.status,
    )
