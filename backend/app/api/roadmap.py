"""
api/roadmap.py
--------------
Career roadmap endpoint.

GET /api/roadmap/{resume_id}
    - Requires authentication (Bearer token)
    - Generates a personalised career roadmap based on resume content
    - Returns recommended technologies, certifications, courses,
      next roles, and a sequential learning plan
    - Persists results in career_roadmaps (upsert)
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.advanced import CareerRoadmap
from app.models.resume import Resume
from app.models.user import User
from app.schemas.advanced import CareerRoadmapResponse, RoadmapStep
from app.services.roadmap_service import generate_roadmap

router = APIRouter(tags=["Career Roadmap"])


@router.get(
    "/{resume_id}",
    response_model=CareerRoadmapResponse,
    summary="Generate a personalised career roadmap",
    description=(
        "Analyses skills and experience to infer a career track (e.g. Data Engineering, "
        "Full-Stack, DevOps) and returns a personalised roadmap including technologies "
        "to learn, certifications, courses, target roles, and a step-by-step learning plan."
    ),
)
def get_career_roadmap(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CareerRoadmapResponse:
    """
    Generate and return a career roadmap for an uploaded resume.

    Access control: users can only generate roadmaps for their own resumes.
    Results are cached in the DB; re-calling regenerates the roadmap.
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
            detail="This resume has no extracted text for roadmap generation.",
        )

    # 2. Generate roadmap
    result = generate_roadmap(resume.extracted_text)

    # Serialise learning roadmap steps to JSON
    steps_json = json.dumps([
        {
            "order": s.order,
            "title": s.title,
            "description": s.description,
            "estimated_time": s.estimated_time,
        }
        for s in result.learning_roadmap
    ])

    # 3. Persist / update in DB (upsert)
    existing = (
        db.query(CareerRoadmap)
        .filter(CareerRoadmap.resume_id == resume_id)
        .first()
    )
    if existing:
        existing.recommended_technologies = json.dumps(result.recommended_technologies)
        existing.certifications           = json.dumps(result.certifications)
        existing.courses                  = json.dumps(result.courses)
        existing.next_roles               = json.dumps(result.next_roles)
        existing.learning_roadmap         = steps_json
    else:
        db.add(CareerRoadmap(
            resume_id=resume_id,
            recommended_technologies=json.dumps(result.recommended_technologies),
            certifications=json.dumps(result.certifications),
            courses=json.dumps(result.courses),
            next_roles=json.dumps(result.next_roles),
            learning_roadmap=steps_json,
        ))
    db.commit()

    # 4. Return response
    return CareerRoadmapResponse(
        resume_id=resume_id,
        current_level=result.current_level,
        target_role=result.target_role,
        recommended_technologies=result.recommended_technologies,
        certifications=result.certifications,
        courses=result.courses,
        next_roles=result.next_roles,
        learning_roadmap=[
            RoadmapStep(
                order=s.order,
                title=s.title,
                description=s.description,
                estimated_time=s.estimated_time,
            )
            for s in result.learning_roadmap
        ],
    )
