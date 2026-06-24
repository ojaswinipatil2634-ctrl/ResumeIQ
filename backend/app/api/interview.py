"""
api/interview.py
----------------
Interview preparation endpoint.

GET /api/interview/{resume_id}
    - Requires authentication (Bearer token)
    - Generates interview questions based on resume content
    - Returns Technical, HR, Project, and Behavioral question categories
    - Persists results in interview_preparations (upsert)

Questions are personalised based on detected skills, experience, and projects.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.advanced import InterviewPreparation
from app.models.resume import Resume
from app.models.user import User
from app.schemas.advanced import InterviewResponse
from app.services.interview_service import generate_interview_questions

router = APIRouter(tags=["Interview Preparation"])


@router.get(
    "/{resume_id}",
    response_model=InterviewResponse,
    summary="Generate interview questions from a resume",
    description=(
        "Generates personalised interview questions based on the resume content. "
        "Returns four categories: Technical (skill-based), HR (culture & fit), "
        "Project (specific to resume projects), and Behavioral (STAR format)."
    ),
)
def get_interview_questions(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewResponse:
    """
    Generate and return interview questions for an uploaded resume.

    Access control: users can only generate questions for their own resumes.
    Results are cached in the DB and regenerated on each call.
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
            detail="This resume has no extracted text for interview preparation.",
        )

    # 2. Generate questions
    result = generate_interview_questions(resume.extracted_text)

    # 3. Persist / update in DB (upsert)
    existing = (
        db.query(InterviewPreparation)
        .filter(InterviewPreparation.resume_id == resume_id)
        .first()
    )
    if existing:
        existing.technical_questions  = json.dumps(result.technical_questions)
        existing.hr_questions         = json.dumps(result.hr_questions)
        existing.project_questions    = json.dumps(result.project_questions)
        existing.behavioral_questions = json.dumps(result.behavioral_questions)
    else:
        db.add(InterviewPreparation(
            resume_id=resume_id,
            technical_questions=json.dumps(result.technical_questions),
            hr_questions=json.dumps(result.hr_questions),
            project_questions=json.dumps(result.project_questions),
            behavioral_questions=json.dumps(result.behavioral_questions),
        ))
    db.commit()

    # 4. Return response
    return InterviewResponse(
        resume_id=resume_id,
        technical_questions=result.technical_questions,
        hr_questions=result.hr_questions,
        project_questions=result.project_questions,
        behavioral_questions=result.behavioral_questions,
        preparation_tips=result.preparation_tips,
    )
