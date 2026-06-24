"""
services/job_match_service.py
------------------------------
Job-description-to-resume matching engine.

Algorithm (all rule-based, no external APIs):
1. Extract skills from the resume text using the existing SKILLS_TAXONOMY.
2. Extract skills and keywords from the job description using the same taxonomy.
3. Compute overlap and gap metrics.
4. Produce a match score and actionable recommendations.

Public API
----------
compute_job_match(resume_text: str, job_description: str) -> JobMatchResult
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

from app.utils.skills_dict import ALL_SKILLS, SKILLS_TAXONOMY


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class JobMatchResult:
    match_score: float
    match_grade: str
    matching_skills: List[str]
    missing_skills: List[str]
    keyword_overlap: Dict[str, List[str]]
    recommendations: List[str]


# ---------------------------------------------------------------------------
# Skill extraction helper (same logic as analysis_service)
# ---------------------------------------------------------------------------

def _extract_skill_set(text: str) -> Set[str]:
    """Return the set of skills found in *text* using word-boundary matching."""
    normalised = text.lower()
    found: Set[str] = set()
    for skill in ALL_SKILLS:
        escaped = re.escape(skill)
        pattern = rf"(?<!\w){escaped}(?!\w)"
        if re.search(pattern, normalised):
            found.add(skill)
    return found


def _categorize_skills(skills: Set[str]) -> Dict[str, List[str]]:
    """Group a set of skills by taxonomy category."""
    result: Dict[str, List[str]] = {}
    for category, cat_skills in SKILLS_TAXONOMY.items():
        matched = [s for s in cat_skills if s in skills]
        if matched:
            result[category] = sorted(matched)
    return result


# ---------------------------------------------------------------------------
# Keyword extraction (beyond the skills taxonomy)
# ---------------------------------------------------------------------------

# Additional domain keywords frequently found in job descriptions
_JD_KEYWORDS = [
    # Soft skills / work style
    "communication", "collaboration", "leadership", "mentoring",
    "problem solving", "critical thinking", "ownership", "initiative",

    # Common JD buzzwords
    "agile", "scrum", "sprint", "kanban", "cross-functional",
    "stakeholders", "roadmap", "okr", "kpi", "metrics",

    # Experience levels
    "senior", "junior", "mid-level", "lead", "principal", "staff",
    "intern", "entry-level",

    # Degree requirements
    "bachelor", "master", "phd", "degree", "computer science",

    # Common requirements
    "open source", "remote", "on-site", "hybrid",
    "full-time", "part-time", "contract",
]


def _extract_jd_keywords(text: str) -> Set[str]:
    """Extract additional non-skill keywords from a job description."""
    lower = text.lower()
    found: Set[str] = set()
    for kw in _JD_KEYWORDS:
        if re.search(rf"(?<!\w){re.escape(kw)}(?!\w)", lower):
            found.add(kw)
    return found


# ---------------------------------------------------------------------------
# Grade mapping
# ---------------------------------------------------------------------------

def _match_grade(score: float) -> str:
    if score >= 80:
        return "Excellent Fit"
    if score >= 60:
        return "Good Fit"
    if score >= 40:
        return "Fair Fit"
    return "Low Fit"


# ---------------------------------------------------------------------------
# Recommendation generator
# ---------------------------------------------------------------------------

def _build_recommendations(
    resume_skills: Set[str],
    jd_skills: Set[str],
    missing: List[str],
    match_score: float,
) -> List[str]:
    recs: List[str] = []

    if missing:
        top_missing = missing[:5]
        recs.append(
            f"Prioritise learning or showcasing these missing skills: "
            f"{', '.join(top_missing)}."
        )

    if match_score < 40:
        recs.append(
            "Your resume matches fewer than 40% of the job requirements. "
            "Consider tailoring the resume specifically for this role by adding "
            "relevant keywords from the job description."
        )
    elif match_score < 60:
        recs.append(
            "Moderate match detected. Add missing skills to your Skills section "
            "and weave relevant keywords into your experience bullet points."
        )
    else:
        recs.append(
            "Strong skill alignment! Make sure to mirror exact phrases from the "
            "job description in your resume to pass ATS filters."
        )

    if len(resume_skills) < 10:
        recs.append(
            "Your resume lists fewer than 10 identifiable skills. "
            "Expand your Skills section to improve ATS match rates."
        )

    recs.append(
        "Use the exact technology names from the job description "
        "(e.g. if they say 'Postgres' not 'PostgreSQL', match that)."
    )

    if match_score >= 70:
        recs.append(
            "Excellent match! Prepare concrete examples (STAR format) for each "
            "matching skill to discuss in the interview."
        )

    return recs


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_job_match(resume_text: str, job_description: str) -> JobMatchResult:
    """
    Compare a resume against a job description and return a match analysis.

    Scoring formula:
        skill_overlap_score  = (matching skills / total JD skills) * 70
        keyword_bonus        = (matching JD keywords / total JD keywords) * 30
        total                = skill_overlap_score + keyword_bonus  (capped at 100)
    """
    resume_skills = _extract_skill_set(resume_text)
    jd_skills     = _extract_skill_set(job_description)

    # Extra keyword pass on the JD
    jd_keywords    = _extract_jd_keywords(job_description)
    resume_keywords = _extract_jd_keywords(resume_text)

    matching_skills = sorted(resume_skills & jd_skills)
    missing_skills  = sorted(jd_skills - resume_skills)

    # Skill overlap component (70% of score)
    if jd_skills:
        skill_ratio = len(matching_skills) / len(jd_skills)
    else:
        skill_ratio = 0.5  # no skills in JD — neutral

    # Keyword overlap component (30% of score)
    if jd_keywords:
        kw_ratio = len(resume_keywords & jd_keywords) / len(jd_keywords)
    else:
        kw_ratio = 0.5

    match_score = round(min((skill_ratio * 70) + (kw_ratio * 30), 100.0), 1)

    # Category-level overlap for the response
    resume_by_cat = _categorize_skills(resume_skills)
    jd_by_cat     = _categorize_skills(jd_skills)
    keyword_overlap: Dict[str, List[str]] = {}
    for cat in jd_by_cat:
        overlap = [s for s in jd_by_cat[cat] if s in resume_skills]
        if overlap:
            keyword_overlap[cat] = overlap

    recommendations = _build_recommendations(
        resume_skills, jd_skills, missing_skills, match_score
    )

    return JobMatchResult(
        match_score=match_score,
        match_grade=_match_grade(match_score),
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        keyword_overlap=keyword_overlap,
        recommendations=recommendations,
    )
