from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.upload import UploadAcceptedResponse
from app.services.upload_validation import validate_upload_metadata


router = APIRouter()


@router.post(
    "/audio",
    response_model=UploadAcceptedResponse,
)
async def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadAcceptedResponse:
    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)

    validate_upload_metadata(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
    )

    return UploadAcceptedResponse(
        job_id=str(uuid4()),
        filename=file.filename or "uploaded-audio",
    )
