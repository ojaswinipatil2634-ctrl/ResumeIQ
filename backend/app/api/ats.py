"""
api/ats.py
----------
ATS (Applicant Tracking System) scoring endpoint.

GET /api/ats/{resume_id}
    - Requires authentication (Bearer token)
    - Fetches the resume (must belong to the current user)
    - Runs the ATS scoring engine on the extracted text
    - Persists the result in ats_analyses (upsert)
    - Returns the scored result with section-wise breakdown

Design note: results are cached in the DB so repeated calls are fast.
To force a re-score, simply call the endpoint again — it overwrites.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.advanced import ATSAnalysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.advanced import ATSResponse, ATSSectionScores
from app.services.ats_service import compute_ats_score

router = APIRouter(tags=["ATS Scoring"])


@router.get(
    "/{resume_id}",
    response_model=ATSResponse,
    summary="Get ATS score for a resume",
    description=(
        "Analyses the resume against ATS criteria and returns an overall score (0–100), "
        "section-wise scores, missing sections, and actionable improvement suggestions."
    ),
)
def get_ats_score(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ATSResponse:
    """
    Run ATS scoring on an uploaded resume.

    Access control: users can only score their own resumes.
    Results are stored in the DB (upserted) to avoid repeated computation.
    """
    # 1. Fetch resume and verify ownership
    resume: Resume | None = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume {resume_id} not found.",
        )
    if not resume.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This resume has no extracted text available for ATS scoring.",
        )

    # 2. Compute ATS score
    result = compute_ats_score(resume.extracted_text)

    # 3. Persist / update in DB (upsert pattern)
    existing = (
        db.query(ATSAnalysis)
        .filter(ATSAnalysis.resume_id == resume_id)
        .first()
    )
    if existing:
        existing.overall_score   = result.overall_score
        existing.section_scores  = json.dumps(result.section_scores)
        existing.missing_sections = json.dumps(result.missing_sections)
        existing.suggestions     = json.dumps(result.suggestions)
    else:
        db.add(ATSAnalysis(
            resume_id=resume_id,
            overall_score=result.overall_score,
            section_scores=json.dumps(result.section_scores),
            missing_sections=json.dumps(result.missing_sections),
            suggestions=json.dumps(result.suggestions),
        ))
    db.commit()

    # 4. Build and return Pydantic response
    return ATSResponse(
        resume_id=resume_id,
        overall_score=result.overall_score,
        grade=result.grade,
        section_scores=ATSSectionScores(**result.section_scores),
        missing_sections=result.missing_sections,
        suggestions=result.suggestions,
    )
