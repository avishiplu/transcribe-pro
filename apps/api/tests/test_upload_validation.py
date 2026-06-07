import pytest
from fastapi import HTTPException

from app.services.upload_validation import (
    MAX_UPLOAD_SIZE_BYTES,
    get_file_extension,
    validate_upload_metadata,
)


def test_get_file_extension_lowercases_extension():
    assert get_file_extension("Lecture.MP3") == ".mp3"


def test_validate_upload_metadata_accepts_supported_audio_file():
    result = validate_upload_metadata(
        filename="lecture.mp3",
        content_type="audio/mpeg",
        size_bytes=1024,
    )

    assert result.filename == "lecture.mp3"
    assert result.extension == ".mp3"


def test_validate_upload_metadata_rejects_missing_filename():
    with pytest.raises(HTTPException) as error:
        validate_upload_metadata(
            filename=None,
            content_type="audio/mpeg",
            size_bytes=1024,
        )

    assert error.value.status_code == 400


def test_validate_upload_metadata_rejects_unsupported_extension():
    with pytest.raises(HTTPException) as error:
        validate_upload_metadata(
            filename="notes.txt",
            content_type="text/plain",
            size_bytes=1024,
        )

    assert error.value.status_code == 400


def test_validate_upload_metadata_rejects_unsupported_content_type():
    with pytest.raises(HTTPException) as error:
        validate_upload_metadata(
            filename="lecture.mp3",
            content_type="application/pdf",
            size_bytes=1024,
        )

    assert error.value.status_code == 400


def test_validate_upload_metadata_rejects_empty_file():
    with pytest.raises(HTTPException) as error:
        validate_upload_metadata(
            filename="lecture.mp3",
            content_type="audio/mpeg",
            size_bytes=0,
        )

    assert error.value.status_code == 400


def test_validate_upload_metadata_rejects_too_large_file():
    with pytest.raises(HTTPException) as error:
        validate_upload_metadata(
            filename="lecture.mp3",
            content_type="audio/mpeg",
            size_bytes=MAX_UPLOAD_SIZE_BYTES + 1,
        )

    assert error.value.status_code == 413
