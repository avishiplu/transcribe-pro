from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid4())


class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    language_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), default="groq", nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False, index=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="transcription_jobs")
    transcript = relationship("Transcript", back_populates="job", uselist=False)
