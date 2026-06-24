"""
schemas/resume.py
------------------
Pydantic models for the resume upload endpoint.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeOut(BaseModel):
    """What we return to the client to describe a stored resume."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    original_filename: str
    file_type: str
    file_size_bytes: int
    uploaded_at: datetime


class ResumeUploadResponse(BaseModel):
    """Response shape for POST /api/resume/upload."""

    resume: ResumeOut
    extracted_text: str
    text_length: int
