"""Local file storage for uploaded documents and generated certificates.

Uploaded files are never stored under their original name. Each file gets a
random UUID name so user-supplied filenames cannot cause path traversal.
"""
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ..config import settings

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}

# Leading bytes ("magic numbers") for each allowed type.
_SIGNATURES = {
    "application/pdf": (b"%PDF",),
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
}

CHUNK_SIZE = 1024 * 1024


def safe_display_name(filename: str | None) -> str:
    """Strip any directory components from a client-supplied filename."""
    name = Path((filename or "document").replace("\\", "/")).name
    return name[:255] or "document"


def save_upload(upload: UploadFile) -> tuple[str, str, int]:
    """Validate and store an upload. Returns (stored_name, content_type, size)."""
    extension = Path(safe_display_name(upload.filename)).suffix.lower()
    content_type = ALLOWED_EXTENSIONS.get(extension)
    if content_type is None:
        raise HTTPException(400, "Only PDF, JPG and PNG files are allowed.")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    stored_name = f"{uuid.uuid4().hex}{extension}"
    target = settings.uploads_dir / stored_name

    size = 0
    header = b""
    try:
        with target.open("wb") as out:
            while chunk := upload.file.read(CHUNK_SIZE):
                if not header:
                    header = chunk[:8]
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        400, f"File is larger than {settings.max_upload_mb} MB."
                    )
                out.write(chunk)
        if size == 0:
            raise HTTPException(400, "File is empty.")
        if not header.startswith(_SIGNATURES[content_type]):
            raise HTTPException(400, "File content does not match its extension.")
    except HTTPException:
        target.unlink(missing_ok=True)
        raise

    return stored_name, content_type, size


def certificate_path(file_name: str) -> Path:
    return settings.certificates_dir / file_name
