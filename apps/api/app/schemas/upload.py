from pydantic import BaseModel, Field


class UploadValidationResult(BaseModel):
    filename: str
    extension: str
    content_type: str
    size_bytes: int = Field(ge=1)


class UploadAcceptedResponse(BaseModel):
    job_id: str
    filename: str
    status: str = "uploaded"
