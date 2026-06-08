from datetime import datetime

from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    job_id: str
    transcript_id: str
    original_filename: str
    status: str
    text: str
    created_at: datetime | None = None
