"""
api/analysis.py
---------------
Resume analysis routes.

GET /api/analysis/{resume_id}
    - Requires authentication (Bearer token)
    - Fetches the resume record (must belong to current user)
    - Runs the NLP analysis pipeline on the stored extracted_text
    - Returns skills, experience summary, education summary,
      career insights, and improvement suggestions

The analysis is computed on the fly and not persisted —
this keeps the DB schema simple and lets us re-run with improved
logic without a migration.  For high traffic, add a Redis cache
keyed on (resume_id, text_hash).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import AnalysisResponse, SkillsOut, ExperienceOut, EducationOut
from app.services.analysis_service import analyse_resume

router = APIRouter(tags=["Analysis"])


@router.get(
    "/{resume_id}",
    response_model=AnalysisResponse,
    summary="Analyse an uploaded resume and return structured insights",
)
def get_analysis(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """
    Run the deterministic NLP analysis pipeline on a stored resume.

    **Access control**: users can only analyse their own resumes.
    A 404 is returned for both "not found" and "not yours" cases to
    avoid leaking the existence of other users' resumes.
    """
    # Fetch resume and verify ownership in a single query
    resume: Resume | None = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume {resume_id} not found",
        )

    if not resume.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This resume has no extracted text available for analysis",
        )

    # Run analysis pipeline (pure Python, no I/O)
    result = analyse_resume(resume.extracted_text)

    return AnalysisResponse(
        resume_id=resume.id,
        extracted_text=resume.extracted_text,
        skills=SkillsOut(
            by_category=result.skills.by_category,
            all_skills=result.skills.all_skills,
        ),
        experience=ExperienceOut(
            raw_text=result.experience.raw_text,
            job_titles=result.experience.job_titles,
            companies=result.experience.companies,
            years_of_experience=result.experience.years_of_experience,
            keywords=result.experience.keywords,
        ),
        education=EducationOut(
            raw_text=result.education.raw_text,
            degrees=result.education.degrees,
            institutions=result.education.institutions,
            fields_of_study=result.education.fields_of_study,
        ),
        career_insights=result.career_insights,
        improvement_suggestions=result.improvement_suggestions,
    )
