"""
api/resume.py
-------------
Resume upload routes.

POST /api/resume/upload
    - Accepts a PDF or DOCX file (multipart/form-data, field name "file")
    - Requires authentication (Bearer token)
    - Saves the file to disk, extracts its text, stores metadata in the DB
    - Returns the extracted text plus resume metadata

If text extraction or the DB write fails after the file is already
saved, the file (and any partial DB row) is cleaned up so we don't
leak orphaned uploads on disk.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeOut, ResumeUploadResponse
from app.utils.file_handler import delete_file, save_upload_file, validate_resume_file
from app.utils.text_extractor import extract_text

router = APIRouter(tags=["Resume"])


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a resume (PDF or DOCX) and extract its text",
)
def upload_resume(
    file: UploadFile = File(..., description="Resume file (.pdf or .docx)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    # 1. Validate extension before touching the disk
    ext = validate_resume_file(file)

    # 2. Stream the file to disk (enforces the size limit while writing)
    stored_filename, file_path, file_size = save_upload_file(file, current_user.id, ext)

    # 3. Extract text — if this fails, remove the file we just saved
    try:
        text = extract_text(file_path, ext)
    except HTTPException:
        delete_file(file_path)
        raise

    # 4. Persist metadata + extracted text, linked to the uploading user
    resume = Resume(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_type=ext.lstrip("."),
        file_size_bytes=file_size,
        extracted_text=text,
    )

    try:
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception as e:
        db.rollback()
        delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save resume metadata: {e}",
        )

    return ResumeUploadResponse(
        resume=ResumeOut.model_validate(resume),
        extracted_text=text,
        text_length=len(text),
    )
