from datetime import datetime

from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    job_id: str
    original_filename: str
    language_code: str | None = None
    provider: str
    status: str
    duration_seconds: float | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
