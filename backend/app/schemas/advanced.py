"""
schemas/advanced.py
--------------------
Pydantic request/response models for Part 5 Advanced AI Career Features.

Covers:
- ATS Scoring
- Job Matching
- Resume Improvement
- Interview Preparation
- Career Roadmap
- Analytics Dashboard
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ── ATS Scoring ───────────────────────────────────────────────────────────────

class ATSSectionScores(BaseModel):
    """Score for each individual resume section (0–100 each)."""
    contact_info: float = Field(description="Score for contact information completeness")
    summary: float = Field(description="Score for professional summary / objective")
    skills: float = Field(description="Score for skills section")
    experience: float = Field(description="Score for work experience section")
    education: float = Field(description="Score for education section")
    projects: float = Field(description="Score for projects section")
    keywords: float = Field(description="Score for ATS keyword density")
    formatting: float = Field(description="Score for resume formatting quality")


class ATSResponse(BaseModel):
    """Full ATS analysis result returned by GET /api/ats/{resume_id}."""
    resume_id: int
    overall_score: float = Field(description="Overall ATS score out of 100")
    grade: str = Field(description="Letter grade: A, B, C, D, F")
    section_scores: ATSSectionScores
    missing_sections: List[str] = Field(description="Sections that are absent from the resume")
    suggestions: List[str] = Field(description="Actionable tips to improve ATS score")


# ── Job Matching ──────────────────────────────────────────────────────────────

class JobMatchRequest(BaseModel):
    """Request body for POST /api/job-match/{resume_id}."""
    job_description: str = Field(
        min_length=50,
        description="Full job description text to match against the resume",
    )


class JobMatchResponse(BaseModel):
    """Job-match analysis result."""
    resume_id: int
    match_score: float = Field(description="Overall match percentage (0–100)")
    match_grade: str = Field(description="Fit level: Excellent / Good / Fair / Low")
    matching_skills: List[str] = Field(description="Skills present in both resume and job description")
    missing_skills: List[str] = Field(description="Skills required by the job but missing from resume")
    keyword_overlap: Dict[str, List[str]] = Field(
        description="Keyword overlap grouped by category"
    )
    recommendations: List[str] = Field(description="Tips to close the gap between resume and JD")


# ── Resume Improvement ────────────────────────────────────────────────────────

class ImprovementSection(BaseModel):
    """Improvement suggestions for a specific area."""
    area: str = Field(description="Area being evaluated (e.g. 'Action Verbs')")
    issues: List[str] = Field(description="Specific problems found")
    tips: List[str] = Field(description="Concrete improvement tips")


class ImprovementResponse(BaseModel):
    """Full improvement analysis returned by GET /api/improve/{resume_id}."""
    resume_id: int
    overall_quality: str = Field(description="Qualitative rating: Excellent / Good / Needs Work / Poor")
    sections: List[ImprovementSection] = Field(description="Per-area improvement suggestions")
    stronger_action_verbs: List[str] = Field(description="Stronger verbs to replace weak ones")
    writing_tips: List[str] = Field(description="General resume writing best practices")


# ── Interview Preparation ─────────────────────────────────────────────────────

class InterviewResponse(BaseModel):
    """Interview questions returned by GET /api/interview/{resume_id}."""
    resume_id: int
    technical_questions: List[str] = Field(description="Technical / skill-based questions")
    hr_questions: List[str] = Field(description="HR and culture-fit questions")
    project_questions: List[str] = Field(description="Questions about specific projects on the resume")
    behavioral_questions: List[str] = Field(
        description="STAR-format behavioral questions (Situation, Task, Action, Result)"
    )
    preparation_tips: List[str] = Field(description="General interview preparation advice")


# ── Career Roadmap ────────────────────────────────────────────────────────────

class RoadmapStep(BaseModel):
    """One step in the learning roadmap."""
    order: int = Field(description="Sequential order (1 = first)")
    title: str = Field(description="Short title of the learning goal")
    description: str = Field(description="What to learn and why")
    estimated_time: str = Field(description="Rough time estimate (e.g. '2–4 weeks')")


class CareerRoadmapResponse(BaseModel):
    """Career roadmap returned by GET /api/roadmap/{resume_id}."""
    resume_id: int
    current_level: str = Field(description="Inferred seniority level (Junior / Mid / Senior)")
    target_role: str = Field(description="Suggested next target role based on the resume")
    recommended_technologies: List[str] = Field(description="Technologies to learn next")
    certifications: List[str] = Field(description="Relevant certifications to pursue")
    courses: List[str] = Field(description="Online courses or learning resources")
    next_roles: List[str] = Field(description="Job titles to target in the next 1–3 years")
    learning_roadmap: List[RoadmapStep] = Field(description="Ordered, step-by-step learning plan")


# ── Analytics Dashboard ───────────────────────────────────────────────────────

class UploadTrend(BaseModel):
    """Daily upload count."""
    date: str = Field(description="Date in YYYY-MM-DD format")
    count: int = Field(description="Number of resumes uploaded on that date")


class DashboardStats(BaseModel):
    """Aggregate statistics returned by GET /api/dashboard/stats."""
    total_users: int
    total_resumes: int
    average_ats_score: Optional[float] = Field(
        None, description="Average ATS score across all analysed resumes; null if none analysed"
    )
    most_common_skills: List[str] = Field(
        description="Top 10 skills found across all resumes (most frequent first)"
    )
    upload_trends: List[UploadTrend] = Field(
        description="Resume upload counts for the last 30 days"
    )
    top_job_titles: List[str] = Field(
        description="Most frequently detected job titles across all resumes"
    )
