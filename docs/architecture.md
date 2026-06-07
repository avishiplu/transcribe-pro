# Transcribe Pro — Architecture Overview

Migration project from `legacy_reference/app.py` (Streamlit) to a production SaaS platform.

## System components

| Component | Technology | Phase |
|-----------|------------|-------|
| API | FastAPI (Python 3.11) | 1 |
| Database | PostgreSQL + SQLAlchemy | 2 |
| Authentication | JWT | 3 |
| File storage | S3-compatible (MinIO dev) | 4 |
| Audio chunking | FFmpeg | 5 |
| Background jobs | Celery + Redis | 6 |
| Transcription | Groq + OpenAI | 6 |
| Payments | Stripe (credits) | 7 |
| Frontend | Next.js | 8 |
| Export | TXT, DOCX | 9–10 |
| Admin | Usage tracking | 11 |
| Production deploy | Docker, CI/CD | 12 |

## API layout

```
apps/api/app/
├── api/routes/       # HTTP endpoints
├── core/             # Config, logging, security (future)
├── db/               # Database session (Phase 2)
├── models/           # SQLAlchemy models (Phase 2)
├── schemas/          # Pydantic request/response models
├── services/         # Business logic (transcription, ffmpeg, etc.)
└── dependencies/     # FastAPI dependency injection (Phase 3)
```

## Legacy logic to port (later phases)

From `legacy_reference/app.py`:

- `WHISPER_LANGUAGES` → `core/languages.py`
- `get_audio_duration_seconds`, `create_safe_audio_chunks_with_ffmpeg` → `services/audio/ffmpeg.py`
- OpenAI / Groq transcription → `services/transcription/`
- Access code concept → user accounts + credit system

## Phase 1 status

Foundation only: health endpoint, config, logging, folder structure. No business logic.
