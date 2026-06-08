from fastapi import APIRouter

from app.api.routes import auth, health, jobs, transcripts, uploads

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
