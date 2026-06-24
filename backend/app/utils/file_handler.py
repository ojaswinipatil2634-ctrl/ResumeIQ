"""
utils/file_handler.py
----------------------
Handles saving uploaded resume files to disk.

Responsibilities:
- Validate file extension
- Stream the file to disk in chunks (never buffers the whole
  upload in memory), enforcing the max-size limit as it writes
- Generate a unique, collision-free filename
- Best-effort cleanup if a later step in the request fails
"""

import os
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

# Bytes read per chunk when streaming the upload to disk
_CHUNK_SIZE = 1024 * 1024  # 1 MB


def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def validate_resume_file(file: UploadFile) -> str:
    """
    Validates the uploaded file's extension.

    Returns the lowercase extension (e.g. ".pdf") on success.
    Raises HTTPException(400) on a missing filename or unsupported type.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    ext = _get_extension(file.filename)
    if ext not in settings.ALLOWED_RESUME_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_RESUME_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed types: {allowed}",
        )

    return ext


def save_upload_file(file: UploadFile, user_id: int, ext: str) -> tuple[str, str, int]:
    """
    Streams *file* to disk under settings.UPLOAD_DIR.

    Returns:
        (stored_filename, absolute_file_path, size_in_bytes)

    Raises:
        HTTPException(413) if the file exceeds MAX_UPLOAD_SIZE_MB.
        HTTPException(400) if the file is empty.
        HTTPException(500) on an unexpected disk error.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    stored_filename = f"user{user_id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    total_written = 0

    try:
        with open(file_path, "wb") as out_file:
            while chunk := file.file.read(_CHUNK_SIZE):
                total_written += len(chunk)
                if total_written > max_bytes:
                    out_file.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit",
                    )
                out_file.write(chunk)
    except HTTPException:
        raise
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}",
        )

    if total_written == 0:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    return stored_filename, os.path.abspath(file_path), total_written


def delete_file(file_path: str) -> None:
    """Best-effort delete — used to clean up if a later step fails."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
