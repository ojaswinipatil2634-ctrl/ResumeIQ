"""
models/resume.py
-----------------
SQLAlchemy ORM model for uploaded resumes.

Each row represents one uploaded file, linked to the user who
uploaded it, plus the text we extracted from it.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    stored_filename: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)  # "pdf" or "docx"
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Resume id={self.id} user_id={self.user_id} file={self.original_filename!r}>"
