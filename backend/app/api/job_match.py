"""
api/job_match.py
----------------
Job-description-to-resume matching endpoint.

POST /api/job-match/{resume_id}
    - Requires authentication (Bearer token)
    - Accepts a job description in the request body
    - Compares the job description against the resume's extracted text
    - Returns match score, matching/missing skills, and recommendations
    - Persists the result in job_match_analyses

Each call creates a new row (users may match the same resume to many JDs).
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.advanced import JobMatchAnalysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.advanced import JobMatchRequest, JobMatchResponse
from app.services.job_match_service import compute_job_match

router = APIRouter(tags=["Job Matching"])


@router.post(
    "/{resume_id}",
    response_model=JobMatchResponse,
    summary="Match a job description against a resume",
    description=(
        "Paste any job description and receive a match score (0–100%), "
        "matched and missing skills, keyword overlap by category, "
        "and personalised recommendations to close the skill gap."
    ),
)
def match_job(
    resume_id: int,
    payload: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobMatchResponse:
    """
    Compare a job description against the resume's extracted text.

    Access control: users can only match their own resumes.
    Each call persists a new job-match record.
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
            detail="This resume has no extracted text for job matching.",
        )

    # 2. Run matching engine
    result = compute_job_match(resume.extracted_text, payload.job_description)

    # 3. Persist result
    record = JobMatchAnalysis(
        resume_id=resume_id,
        match_score=result.match_score,
        job_description_snippet=payload.job_description[:500],
        matching_skills=json.dumps(result.matching_skills),
        missing_skills=json.dumps(result.missing_skills),
        recommendations=json.dumps(result.recommendations),
    )
    db.add(record)
    db.commit()

    # 4. Return response
    return JobMatchResponse(
        resume_id=resume_id,
        match_score=result.match_score,
        match_grade=result.match_grade,
        matching_skills=result.matching_skills,
        missing_skills=result.missing_skills,
        keyword_overlap=result.keyword_overlap,
        recommendations=result.recommendations,
    )
