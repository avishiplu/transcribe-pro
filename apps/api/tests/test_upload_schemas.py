from app.schemas.upload import UploadAcceptedResponse, UploadValidationResult


def test_upload_validation_result_accepts_audio_metadata():
    result = UploadValidationResult(
        filename="lecture.mp3",
        extension=".mp3",
        content_type="audio/mpeg",
        size_bytes=1024,
    )

    assert result.filename == "lecture.mp3"
    assert result.extension == ".mp3"
    assert result.content_type == "audio/mpeg"
    assert result.size_bytes == 1024


def test_upload_accepted_response_defaults_to_uploaded_status():
    response = UploadAcceptedResponse(
        job_id="job-123",
        filename="lecture.mp3",
    )

    assert response.status == "uploaded"
