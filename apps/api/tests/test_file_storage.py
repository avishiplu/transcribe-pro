from io import BytesIO

from starlette.datastructures import UploadFile

from app.services.file_storage import save_uploaded_audio_file


def test_save_uploaded_audio_file_creates_file_in_storage_dir(tmp_path):
    upload_file = UploadFile(
        file=BytesIO(b"fake audio content"),
        filename="lecture.mp3",
    )

    stored_file_path = save_uploaded_audio_file(
        file=upload_file,
        extension="mp3",
        storage_dir=tmp_path,
    )

    saved_files = list(tmp_path.iterdir())

    assert len(saved_files) == 1
    assert saved_files[0].suffix == ".mp3"
    assert saved_files[0].read_bytes() == b"fake audio content"
    assert stored_file_path.endswith(".mp3")
