from pathlib import Path
from typing import Any

from openai import BadRequestError, OpenAI

from app.core.config import settings


class GroqApiKeyMissingError(RuntimeError):
    pass


def get_groq_client() -> OpenAI:
    if not settings.groq_api_key:
        raise GroqApiKeyMissingError("GROQ_API_KEY is not configured")

    return OpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
    )


def extract_transcription_text(transcription_response: Any) -> str:
    text = getattr(transcription_response, "text", None)

    if isinstance(text, str):
        return text

    if isinstance(transcription_response, str):
        return transcription_response

    raise ValueError("Transcription response does not contain text")


def transcribe_audio_with_groq(
    *,
    file_path: Path,
    language_code: str | None = None,
    client: Any | None = None,
    model: str | None = None,
) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    active_client = client if client is not None else get_groq_client()
    active_model = model if model is not None else settings.groq_transcription_model

    with file_path.open("rb") as audio_file:
        kwargs: dict[str, Any] = {
            "model": active_model,
            "file": audio_file,
        }

        if language_code:
            kwargs["language"] = language_code

        try:
            response = active_client.audio.transcriptions.create(**kwargs)
        except BadRequestError as error:
            error_detail = str(error)

            response = getattr(error, "response", None)
            if response is not None:
                try:
                    error_detail = response.text
                except Exception:
                    error_detail = str(error)

            raise RuntimeError(f"Groq transcription request failed: {error_detail}") from error

    return extract_transcription_text(response)
