"""
models/advanced.py
------------------
SQLAlchemy ORM models for Part 5 Advanced AI Career Features.

Tables created:
- ats_analyses        : stores ATS score results per resume
- job_match_analyses  : stores job-matching results per resume + job description
- interview_preps     : stores generated interview questions per resume
- career_roadmaps     : stores generated career roadmap per resume

All tables link to the resumes table via resume_id foreign key.
JSON columns store the structured analysis data as text (SQLite-compatible).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ATSAnalysis(Base):
    """
    Stores a cached ATS score analysis for a resume.
    One row per resume (upsert pattern — overwrite on re-run).
    """
    __tablename__ = "ats_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False, index=True, unique=True,   # one analysis per resume
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)

    # JSON strings — stored as Text in SQLite, parsed in the service layer
    section_scores: Mapped[str] = mapped_column(Text, nullable=False)   # {section: score}
    missing_sections: Mapped[str] = mapped_column(Text, nullable=False) # [section, …]
    suggestions: Mapped[str] = mapped_column(Text, nullable=False)      # [tip, …]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<ATSAnalysis resume_id={self.resume_id} score={self.overall_score}>"


class JobMatchAnalysis(Base):
    """
    Stores one job-match analysis result.
    Multiple rows per resume are allowed (different job descriptions).
    """
    __tablename__ = "job_match_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    match_score: Mapped[float] = mapped_column(Float, nullable=False)

    job_description_snippet: Mapped[str] = mapped_column(Text, nullable=False)  # first 500 chars
    matching_skills: Mapped[str] = mapped_column(Text, nullable=False)   # JSON list
    missing_skills: Mapped[str] = mapped_column(Text, nullable=False)    # JSON list
    recommendations: Mapped[str] = mapped_column(Text, nullable=False)   # JSON list

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<JobMatchAnalysis resume_id={self.resume_id} score={self.match_score}>"


class InterviewPreparation(Base):
    """
    Stores generated interview questions for a resume.
    One row per resume (upsert on re-run).
    """
    __tablename__ = "interview_preparations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False, index=True, unique=True,
    )

    # Each field is a JSON list of question strings
    technical_questions: Mapped[str] = mapped_column(Text, nullable=False)
    hr_questions: Mapped[str] = mapped_column(Text, nullable=False)
    project_questions: Mapped[str] = mapped_column(Text, nullable=False)
    behavioral_questions: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<InterviewPreparation resume_id={self.resume_id}>"


class CareerRoadmap(Base):
    """
    Stores a generated career roadmap for a resume.
    One row per resume (upsert on re-run).
    """
    __tablename__ = "career_roadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False, index=True, unique=True,
    )

    # All JSON lists / objects stored as Text
    recommended_technologies: Mapped[str] = mapped_column(Text, nullable=False)
    certifications: Mapped[str] = mapped_column(Text, nullable=False)
    courses: Mapped[str] = mapped_column(Text, nullable=False)
    next_roles: Mapped[str] = mapped_column(Text, nullable=False)
    learning_roadmap: Mapped[str] = mapped_column(Text, nullable=False)  # ordered list of steps

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<CareerRoadmap resume_id={self.resume_id}>"
