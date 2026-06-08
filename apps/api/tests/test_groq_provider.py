from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.transcription.groq_provider import (
    GroqApiKeyMissingError,
    extract_transcription_text,
    get_groq_client,
    transcribe_audio_with_groq,
)


class DummyTranscriptions:
    def __init__(self):
        self.kwargs = None
        self.file_bytes = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        self.file_bytes = kwargs["file"].read()
        return SimpleNamespace(text="Hello from Groq")


class DummyAudio:
    def __init__(self):
        self.transcriptions = DummyTranscriptions()


class DummyClient:
    def __init__(self):
        self.audio = DummyAudio()


def test_extract_transcription_text_from_object():
    response = SimpleNamespace(text="Hello world")

    assert extract_transcription_text(response) == "Hello world"


def test_extract_transcription_text_from_string():
    assert extract_transcription_text("Hello string") == "Hello string"


def test_get_groq_client_requires_api_key():
    with pytest.raises(GroqApiKeyMissingError):
        get_groq_client()


def test_transcribe_audio_with_groq_uses_client_and_returns_text(tmp_path):
    audio_path = tmp_path / "lecture.mp3"
    audio_path.write_bytes(b"fake audio bytes")

    client = DummyClient()

    text = transcribe_audio_with_groq(
        file_path=audio_path,
        language_code="en",
        client=client,
        model="test-model",
    )

    assert text == "Hello from Groq"
    assert client.audio.transcriptions.kwargs["model"] == "test-model"
    assert client.audio.transcriptions.kwargs["language"] == "en"
    assert client.audio.transcriptions.file_bytes == b"fake audio bytes"


def test_transcribe_audio_with_groq_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        transcribe_audio_with_groq(
            file_path=Path("missing-audio.mp3"),
            client=DummyClient(),
            model="test-model",
        )
