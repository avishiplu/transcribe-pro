import asyncio

from app.db.session import async_session_maker
from app.repositories.transcription_jobs import get_next_queued_transcription_job
from app.services.transcription.job_processor import process_transcription_job


async def main() -> None:
    async with async_session_maker() as db:
        job = await get_next_queued_transcription_job(db)

        if job is None:
            print("No queued transcription job found.")
            return

        print(f"Processing job: {job.id}")
        print(f"Original filename: {job.original_filename}")
        print(f"Stored file path: {job.stored_file_path}")

        transcript = await process_transcription_job(
            db=db,
            job=job,
        )

        print("Transcription completed.")
        print(f"Transcript ID: {transcript.id}")
        print("Transcript preview:")
        print(transcript.text[:500])


if __name__ == "__main__":
    asyncio.run(main())
