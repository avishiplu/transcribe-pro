# Transcribe Pro Backend

Professional audio transcription platform — migrated from the legacy Streamlit prototype.

## Project structure

```
transcribe-pro-backend/
├── legacy_reference/   # Original Streamlit app (read-only reference)
├── apps/
│   └── api/            # FastAPI backend (Phase 1)
├── infra/docker/       # Docker Compose for local development
└── docs/               # Architecture documentation
```

## Phase 1 — current scope

- FastAPI server with versioned API (`/api/v1`)
- Health check endpoint
- Configuration and structured logging
- Folder placeholders for future phases (db, auth, upload, transcription, etc.)

**Not implemented yet:** database, authentication, payments, file upload, transcription, background workers, frontend.

## Quick start (local)

### 1. Create virtual environment

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp ../../.env.example ../../.env
```

### 3. Run the API

From `apps/api`:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify

- Health: http://127.0.0.1:8000/api/v1/health
- API docs: http://127.0.0.1:8000/docs

### 5. Run tests

From `apps/api`:

```bash
pytest
```

## Docker (optional)

From the repository root:

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

## Legacy reference

The original Streamlit prototype lives in `legacy_reference/`. Do not modify it. Transcription logic will be ported into `apps/api/app/services/` in later phases.
