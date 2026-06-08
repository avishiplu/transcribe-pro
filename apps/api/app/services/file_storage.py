from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile


API_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_STORAGE_DIR = API_ROOT / "storage" / "uploads" / "originals"


def save_uploaded_audio_file(
    file: UploadFile,
    extension: str,
    storage_dir: Path = UPLOAD_STORAGE_DIR,
) -> str:
    storage_dir.mkdir(parents=True, exist_ok=True)

    safe_extension = extension.lower().lstrip(".")
    stored_filename = f"{uuid4()}.{safe_extension}"
    stored_path = storage_dir / stored_filename

    file.file.seek(0)

    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file.file.seek(0)

    try:
        return stored_path.relative_to(API_ROOT).as_posix()
    except ValueError:
        return stored_path.as_posix()
