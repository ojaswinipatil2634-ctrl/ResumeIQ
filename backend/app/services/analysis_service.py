"""
services/analysis_service.py
-----------------------------
Deterministic NLP analysis of a resume's extracted text.

All logic is rule-based (regex + keyword matching) — no ML models,
no external AI APIs.  Fast, explainable, and easy to extend.

Public entry point
------------------
analyse_resume(text: str) -> AnalysisResult
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List

from app.utils.resume_parser import parse_sections
from app.utils.skills_dict import ALL_SKILLS, SKILLS_TAXONOMY

# ---------------------------------------------------------------------------
# Data classes (plain Python — Pydantic schemas are in schemas/analysis.py)
# ---------------------------------------------------------------------------

@dataclass
class SkillsResult:
    by_category: Dict[str, List[str]]   # e.g. {"Programming Languages": ["python", …]}
    all_skills: List[str]               # flat sorted list


@dataclass
class ExperienceSummary:
    raw_text: str
    job_titles: List[str]
    companies: List[str]
    years_of_experience: int | None     # best-effort estimate
    keywords: List[str]


@dataclass
class EducationSummary:
    raw_text: str
    degrees: List[str]
    institutions: List[str]
    fields_of_study: List[str]


@dataclass
class AnalysisResult:
    skills: SkillsResult
    experience: ExperienceSummary
    education: EducationSummary
    career_insights: List[str]
    improvement_suggestions: List[str]


# ---------------------------------------------------------------------------
# Skills extraction
# ---------------------------------------------------------------------------

def _extract_skills(text: str) -> SkillsResult:
    """
    Scan *text* for every skill in ALL_SKILLS (longest-first to avoid
    double-counting).  Uses word-boundary matching so "c" won't match
    inside "react".
    """
    normalised = text.lower()
    found: set[str] = set()

    for skill in ALL_SKILLS:
        # Build a pattern that handles multi-word skills and word boundaries
        escaped = re.escape(skill)
        pattern = rf"(?<!\w){escaped}(?!\w)"
        if re.search(pattern, normalised):
            found.add(skill)

    # Group by category (preserves taxonomy order)
    by_category: Dict[str, List[str]] = {}
    for category, skills in SKILLS_TAXONOMY.items():
        matched = [s for s in skills if s in found]
        if matched:
            by_category[category] = sorted(matched)

    return SkillsResult(
        by_category=by_category,
        all_skills=sorted(found),
    )


# ---------------------------------------------------------------------------
# Experience extraction
# ---------------------------------------------------------------------------

# Common job-title words — used to pull title-like lines from experience text
_TITLE_KEYWORDS = [
    "engineer", "developer", "architect", "manager", "lead", "head",
    "director", "analyst", "consultant", "designer", "scientist",
    "intern", "associate", "senior", "junior", "staff", "principal",
    "vp", "cto", "ceo", "coo", "president", "officer",
]

# Patterns for year ranges, e.g. "2018 – 2021", "Jan 2020 - Present"
_YEAR_RANGE_RE = re.compile(
    r"\b(19|20)\d{2}\b\s*[-–—to]+\s*(\b(19|20)\d{2}\b|present|current|now)",
    re.IGNORECASE,
)
_SINGLE_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

# Company indicators
_COMPANY_INDICATORS = [
    "inc", "ltd", "llc", "corp", "co.", "company", "technologies",
    "solutions", "services", "group", "labs", "studio", "agency",
]

# High-value experience keywords recruiters care about
_EXP_KEYWORDS = [
    "led", "built", "designed", "architected", "improved", "reduced",
    "increased", "launched", "delivered", "managed", "mentored",
    "optimised", "optimized", "migrated", "integrated", "automated",
    "deployed", "scaled", "owned", "collaborated", "shipped",
    "implemented", "developed", "created", "established", "drove",
]


def _estimate_years(text: str) -> int | None:
    """
    Sum the spans from all year-range matches in *text*.
    Returns None if no ranges are found.
    """
    total = 0
    found_any = False
    current_year = 2025  # deterministic baseline

    for m in _YEAR_RANGE_RE.finditer(text):
        start_str = re.search(r"\b(19|20)\d{2}\b", m.group())
        end_str = re.search(
            r"present|current|now|\b(19|20)\d{2}\b",
            m.group()[4:],   # skip the start year
            re.IGNORECASE,
        )
        if not start_str:
            continue
        start = int(start_str.group())
        end_match = end_str.group() if end_str else None
        if end_match and re.match(r"present|current|now", end_match, re.IGNORECASE):
            end = current_year
        elif end_match:
            end = int(end_match)
        else:
            continue
        if end >= start:
            total += end - start
            found_any = True

    return total if found_any else None


def _extract_job_titles(text: str) -> List[str]:
    titles = []
    for line in text.splitlines():
        lower = line.lower()
        if any(kw in lower for kw in _TITLE_KEYWORDS):
            clean = line.strip(" •·-–—\t")
            if clean and len(clean) < 80:
                titles.append(clean)
    return list(dict.fromkeys(titles))[:8]  # deduplicate, cap at 8


def _extract_companies(text: str) -> List[str]:
    companies = []
    for line in text.splitlines():
        lower = line.lower()
        if any(ind in lower for ind in _COMPANY_INDICATORS):
            clean = line.strip(" •·-–—\t")
            if clean and len(clean) < 80:
                companies.append(clean)
    return list(dict.fromkeys(companies))[:8]


def _extract_experience(sections: Dict[str, str]) -> ExperienceSummary:
    exp_text = sections.get("experience", "") or sections.get("__preamble__", "")

    keywords_found = []
    normalised = exp_text.lower()
    for kw in _EXP_KEYWORDS:
        if re.search(rf"\b{kw}\w*\b", normalised):
            keywords_found.append(kw)

    return ExperienceSummary(
        raw_text=exp_text[:2000],   # cap for response size
        job_titles=_extract_job_titles(exp_text),
        companies=_extract_companies(exp_text),
        years_of_experience=_estimate_years(exp_text),
        keywords=sorted(set(keywords_found)),
    )


# ---------------------------------------------------------------------------
# Education extraction
# ---------------------------------------------------------------------------

_DEGREE_PATTERNS = [
    (r"\bph\.?d\.?\b", "PhD"),
    (r"\bdoctor(?:ate)?\b", "Doctorate"),
    (r"\bmaster(?:'s|s)?\b|\bm\.?sc\.?\b|\bm\.?eng\.?\b|\bm\.?b\.?a\.?\b", "Master's"),
    (r"\bbachelor(?:'s|s)?\b|\bb\.?sc\.?\b|\bb\.?eng\.?\b|\bb\.?a\.?\b", "Bachelor's"),
    (r"\bassociate(?:'s|s)?\b", "Associate's"),
    (r"\bdiploma\b", "Diploma"),
    (r"\bcertificate\b", "Certificate"),
    (r"\bhigh school\b|\bsecondary school\b|\bgsces?\b|\ba[- ]levels?\b", "High School"),
]

_FIELD_KEYWORDS = [
    "computer science", "software engineering", "information technology",
    "electrical engineering", "mechanical engineering", "civil engineering",
    "data science", "mathematics", "physics", "business administration",
    "finance", "accounting", "economics", "psychology", "biology",
    "chemistry", "communications", "marketing", "management",
]

# Lines that look like university/college names
_INSTITUTION_INDICATORS = [
    "university", "college", "institute", "school", "academy",
    "polytechnic", "faculty",
]


def _extract_degrees(text: str) -> List[str]:
    found = []
    lower = text.lower()
    for pattern, label in _DEGREE_PATTERNS:
        if re.search(pattern, lower, re.IGNORECASE):
            found.append(label)
    return list(dict.fromkeys(found))


def _extract_institutions(text: str) -> List[str]:
    results = []
    for line in text.splitlines():
        if any(ind in line.lower() for ind in _INSTITUTION_INDICATORS):
            clean = line.strip(" •·-–—\t")
            if clean and len(clean) < 100:
                results.append(clean)
    return list(dict.fromkeys(results))[:5]


def _extract_fields(text: str) -> List[str]:
    lower = text.lower()
    return [f for f in _FIELD_KEYWORDS if f in lower]


def _extract_education(sections: Dict[str, str]) -> EducationSummary:
    edu_text = sections.get("education", "")
    return EducationSummary(
        raw_text=edu_text[:1000],
        degrees=_extract_degrees(edu_text),
        institutions=_extract_institutions(edu_text),
        fields_of_study=_extract_fields(edu_text),
    )


# ---------------------------------------------------------------------------
# Career insights & improvement suggestions
# ---------------------------------------------------------------------------

def _generate_insights(
    skills: SkillsResult,
    experience: ExperienceSummary,
    education: EducationSummary,
) -> List[str]:
    insights: List[str] = []
    cats = skills.by_category

    # Role inference
    prog = cats.get("Programming Languages", [])
    web = cats.get("Web & Frontend", [])
    data = cats.get("Data & ML", [])
    cloud = cats.get("Cloud & DevOps", [])
    backend = cats.get("Backend & APIs", [])

    if data and prog:
        insights.append(
            "Your profile shows a strong data-oriented focus — roles like "
            "Data Engineer, ML Engineer, or Data Scientist would be a natural fit."
        )
    if web and backend:
        insights.append(
            "You have both frontend and backend skills, making you a strong "
            "full-stack candidate."
        )
    elif web and not backend:
        insights.append(
            "Your skills lean toward frontend development — Frontend Engineer "
            "or UI/UX Engineer roles align well."
        )
    elif backend and not web:
        insights.append(
            "Your profile points toward backend or API-focused engineering roles."
        )
    if cloud:
        insights.append(
            f"Cloud experience detected ({', '.join(cloud[:3])}) — "
            "DevOps or Platform Engineering roles are within reach."
        )
    if experience.years_of_experience is not None:
        yoe = experience.years_of_experience
        if yoe < 2:
            insights.append("Early-career profile — targeting junior or associate roles is appropriate.")
        elif yoe < 5:
            insights.append(f"~{yoe} years of experience detected — mid-level roles are a strong match.")
        else:
            insights.append(
                f"~{yoe} years of experience detected — senior or lead roles are well within reach."
            )
    if "leadership" in skills.all_skills or any(
        kw in experience.keywords for kw in ["led", "managed", "mentored"]
    ):
        insights.append(
            "Leadership signals found — you may be competitive for team lead "
            "or engineering manager positions."
        )

    if not insights:
        insights.append(
            "A solid generalist profile. Highlighting specific impact metrics "
            "will help differentiate you."
        )

    return insights


def _generate_suggestions(
    skills: SkillsResult,
    experience: ExperienceSummary,
    education: EducationSummary,
    full_text: str,
) -> List[str]:
    suggestions: List[str] = []
    cats = skills.by_category
    lower = full_text.lower()

    # Quantified impact
    has_numbers = bool(re.search(r"\d+\s*%|\$\d+|\d+x\b|\d+\s*(?:users|customers|engineers|team)", lower))
    if not has_numbers:
        suggestions.append(
            "Add quantified achievements (e.g. 'reduced latency by 40%', "
            "'grew user base to 10 k') — numbers make your impact concrete."
        )

    # Missing sections
    if not experience.job_titles:
        suggestions.append(
            "Job titles are hard to detect — use clear headings like "
            "'Software Engineer at Acme Corp (2021–2023)'."
        )
    if not education.degrees:
        suggestions.append(
            "No degree information found — if you have a degree, add it to "
            "an Education section."
        )

    # Skill gaps for common tracks
    prog = cats.get("Programming Languages", [])
    if prog and not cats.get("Testing & QA"):
        suggestions.append(
            "No testing skills detected — adding pytest, Jest, or similar "
            "signals engineering maturity to reviewers."
        )
    if prog and not cats.get("Cloud & DevOps"):
        suggestions.append(
            "Cloud/DevOps skills (Docker, AWS, CI/CD) are expected for most "
            "modern engineering roles — consider adding any you have."
        )
    if not cats.get("Tools & Practices"):
        suggestions.append(
            "Mentioning Agile/Scrum, Git workflow, or code-review practices "
            "adds credibility."
        )

    # Action verbs
    if len(experience.keywords) < 3:
        suggestions.append(
            "Use strong action verbs (built, led, optimised, delivered) to "
            "open bullet points in your experience section."
        )

    # Length heuristic
    word_count = len(full_text.split())
    if word_count < 200:
        suggestions.append(
            "Your resume looks short — aim for 400–700 words for a 1-page resume."
        )
    elif word_count > 1200:
        suggestions.append(
            "Your resume may be too long — consider trimming to 1–2 pages."
        )

    return suggestions


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyse_resume(text: str) -> AnalysisResult:
    """
    Full analysis pipeline for a resume's extracted text.

    Steps:
    1. Parse the text into logical sections.
    2. Extract skills via keyword matching.
    3. Extract experience metadata (titles, companies, years).
    4. Extract education metadata (degrees, institutions, fields).
    5. Generate career insights and improvement suggestions.
    """
    sections = parse_sections(text)
    skills = _extract_skills(text)
    experience = _extract_experience(sections)
    education = _extract_education(sections)
    insights = _generate_insights(skills, experience, education)
    suggestions = _generate_suggestions(skills, experience, education, text)

    return AnalysisResult(
        skills=skills,
        experience=experience,
        education=education,
        career_insights=insights,
        improvement_suggestions=suggestions,
    )
