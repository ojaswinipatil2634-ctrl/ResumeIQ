"""
api/improvement.py
------------------
Resume improvement suggestions endpoint.

GET /api/improve/{resume_id}
    - Requires authentication (Bearer token)
    - Fetches the resume (must belong to current user)
    - Runs the improvement analysis engine
    - Returns per-area suggestions, stronger action verbs, and writing tips

Results are NOT cached (always fresh analysis on each call).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.advanced import ImprovementResponse, ImprovementSection
from app.services.improvement_service import generate_improvements

router = APIRouter(tags=["Resume Improvement"])


@router.get(
    "/{resume_id}",
    response_model=ImprovementResponse,
    summary="Get resume improvement suggestions",
    description=(
        "Analyses the resume for weak action verbs, generic wording, missing "
        "achievements, and poor structure. Returns concrete, actionable suggestions "
        "along with stronger alternative verbs and general writing tips."
    ),
)
def get_improvements(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ImprovementResponse:
    """
    Run the improvement analysis pipeline on an uploaded resume.

    Access control: users can only improve their own resumes.
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
            detail="This resume has no extracted text available for improvement analysis.",
        )

    # 2. Generate improvements
    result = generate_improvements(resume.extracted_text)

    # 3. Build response
    return ImprovementResponse(
        resume_id=resume_id,
        overall_quality=result.overall_quality,
        sections=[
            ImprovementSection(
                area=s.area,
                issues=s.issues,
                tips=s.tips,
            )
            for s in result.sections
        ],
        stronger_action_verbs=result.stronger_action_verbs,
        writing_tips=result.writing_tips,
    )
