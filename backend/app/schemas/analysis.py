"""
schemas/analysis.py
--------------------
Pydantic response schemas for the resume analysis endpoint.

AnalysisResponse is the top-level model returned by
GET /api/analysis/{resume_id}.
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class SkillsOut(BaseModel):
    by_category: Dict[str, List[str]] = Field(
        description="Skills grouped by category (e.g. 'Programming Languages': ['python', 'go'])"
    )
    all_skills: List[str] = Field(
        description="Flat alphabetical list of every detected skill"
    )


class ExperienceOut(BaseModel):
    raw_text: str = Field(description="Raw text of the experience section (truncated to 2 000 chars)")
    job_titles: List[str] = Field(description="Detected job-title lines")
    companies: List[str] = Field(description="Detected company-name lines")
    years_of_experience: int | None = Field(
        None, description="Best-effort total years derived from date ranges; null if undetermined"
    )
    keywords: List[str] = Field(description="High-value action/impact keywords found in the section")


class EducationOut(BaseModel):
    raw_text: str = Field(description="Raw text of the education section (truncated to 1 000 chars)")
    degrees: List[str] = Field(description="Degree levels detected (e.g. 'Bachelor's', 'Master's')")
    institutions: List[str] = Field(description="University / college name lines")
    fields_of_study: List[str] = Field(description="Academic fields detected")


class AnalysisResponse(BaseModel):
    resume_id: int
    extracted_text: str = Field(description="Full extracted text of the resume")
    skills: SkillsOut
    experience: ExperienceOut
    education: EducationOut
    career_insights: List[str] = Field(
        description="Rule-based observations about the candidate's profile and likely career direction"
    )
    improvement_suggestions: List[str] = Field(
        description="Actionable tips to strengthen the resume"
    )

    model_config = {"from_attributes": True}
