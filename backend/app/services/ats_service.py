"""
services/ats_service.py
------------------------
ATS (Applicant Tracking System) scoring engine.

All logic is rule-based — no external APIs or ML models.
Each section of the resume is scored independently on a 0–100 scale,
then a weighted average produces the overall ATS score.

Public API
----------
compute_ats_score(text: str) -> ATSScoreResult
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# Result dataclass (internal — converted to Pydantic in the router)
# ---------------------------------------------------------------------------

@dataclass
class ATSScoreResult:
    overall_score: float
    grade: str
    section_scores: Dict[str, float]
    missing_sections: List[str]
    suggestions: List[str]


# ---------------------------------------------------------------------------
# Section weights  (must sum to 1.0)
# ---------------------------------------------------------------------------

_WEIGHTS = {
    "contact_info": 0.15,
    "summary":      0.10,
    "skills":       0.15,
    "experience":   0.25,
    "education":    0.15,
    "projects":     0.10,
    "keywords":     0.05,
    "formatting":   0.05,
}


# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Contact info patterns
_EMAIL_RE    = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE    = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
_GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)

# Section heading detector (mirrors resume_parser logic)
_HEADING_RE = re.compile(
    r"^\s*("
    r"summary|profile|objective|about me|"
    r"experience|work experience|employment|"
    r"education|academic|qualifications?|"
    r"skills?|technical skills?|competencies|technologies|"
    r"projects?|portfolio|"
    r"certifications?|certificates?|"
    r"languages?|interests?"
    r")\s*[:\-–—]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Action verbs that look good to ATS
_ACTION_VERBS = [
    "led", "built", "designed", "architected", "improved", "reduced",
    "increased", "launched", "delivered", "managed", "mentored",
    "optimised", "optimized", "migrated", "integrated", "automated",
    "deployed", "scaled", "implemented", "developed", "created",
    "established", "drove", "owned", "shipped", "collaborated",
]

# Quantified-impact patterns  (e.g. "40%", "$1M", "3x", "200 users")
_METRIC_RE = re.compile(
    r"\d+\s*%|\$\s*\d+|\d+\s*[xX]\b|\d+\s*(users?|customers?|engineers?|"
    r"clients?|products?|services?|applications?|systems?)"
)

# ATS-friendly skill keywords (sampled from skills_dict)
_ATS_KEYWORDS = [
    "python", "javascript", "java", "sql", "aws", "azure", "docker",
    "kubernetes", "react", "node.js", "machine learning", "data analysis",
    "agile", "scrum", "git", "ci/cd", "api", "rest", "microservices",
    "tensorflow", "pytorch", "fastapi", "django", "flask",
]


# ---------------------------------------------------------------------------
# Individual scorers
# ---------------------------------------------------------------------------

def _score_contact_info(text: str) -> tuple[float, List[str]]:
    """Check for email, phone, LinkedIn, GitHub."""
    score = 0.0
    tips: List[str] = []

    if _EMAIL_RE.search(text):
        score += 40
    else:
        tips.append("Add a professional email address to your resume.")

    if _PHONE_RE.search(text):
        score += 30
    else:
        tips.append("Add your phone number so recruiters can reach you.")

    if _LINKEDIN_RE.search(text):
        score += 20
    else:
        tips.append("Add your LinkedIn profile URL (linkedin.com/in/yourname).")

    if _GITHUB_RE.search(text):
        score += 10
    else:
        tips.append("Include your GitHub URL to showcase your code portfolio.")

    return min(score, 100.0), tips


def _score_summary(text: str, sections: Dict[str, str]) -> tuple[float, List[str]]:
    """Checks for a summary/objective section with enough content."""
    tips: List[str] = []
    summary_text = sections.get("summary", "")

    if not summary_text:
        return 0.0, ["Add a professional summary or objective section (3–5 sentences)."]

    words = len(summary_text.split())
    if words < 20:
        score = 40.0
        tips.append("Expand your summary to at least 3–5 sentences to give context.")
    elif words < 60:
        score = 75.0
    else:
        score = 100.0

    return score, tips


def _score_skills(text: str, sections: Dict[str, str]) -> tuple[float, List[str]]:
    """Checks skills section exists and has enough items."""
    tips: List[str] = []
    skills_text = sections.get("skills", "")

    if not skills_text:
        return 0.0, ["Add a dedicated Skills section listing your technical and soft skills."]

    # Count comma/bullet/newline separated items
    items = re.split(r"[,|\n•·\-–]", skills_text)
    items = [i.strip() for i in items if i.strip() and len(i.strip()) > 1]
    count = len(items)

    if count < 5:
        score = 40.0
        tips.append("List at least 8–12 specific skills — be explicit about tools and technologies.")
    elif count < 10:
        score = 70.0
        tips.append("Add more skills; recruiters scan for specific keywords.")
    else:
        score = 100.0

    return score, tips


def _score_experience(text: str, sections: Dict[str, str]) -> tuple[float, List[str]]:
    """Scores the experience section for depth and quality."""
    tips: List[str] = []
    exp_text = sections.get("experience", "")

    if not exp_text:
        return 0.0, [
            "Add a Work Experience section with job titles, company names, dates, and bullet points."
        ]

    score = 30.0  # base for having the section

    # Action verbs
    lower = exp_text.lower()
    verbs_found = [v for v in _ACTION_VERBS if re.search(rf"\b{v}\w*\b", lower)]
    if len(verbs_found) >= 5:
        score += 30
    elif len(verbs_found) >= 2:
        score += 15
        tips.append("Use more strong action verbs (led, built, optimised) to begin bullet points.")
    else:
        tips.append("Begin each bullet point with a powerful action verb (built, launched, reduced).")

    # Quantified achievements
    metrics = _METRIC_RE.findall(exp_text)
    if len(metrics) >= 3:
        score += 25
    elif len(metrics) >= 1:
        score += 10
        tips.append("Quantify more achievements with numbers, percentages, or dollar amounts.")
    else:
        tips.append(
            "Add at least 2–3 quantified results (e.g. 'reduced load time by 35%') "
            "— numbers dramatically improve ATS ranking."
        )

    # Date ranges
    date_re = re.compile(r"\b(19|20)\d{2}\b")
    dates = date_re.findall(exp_text)
    if len(dates) >= 2:
        score += 15
    else:
        tips.append("Include start and end dates for each role (e.g. Jan 2021 – Mar 2023).")

    return min(score, 100.0), tips


def _score_education(text: str, sections: Dict[str, str]) -> tuple[float, List[str]]:
    """Scores the education section."""
    tips: List[str] = []
    edu_text = sections.get("education", "")

    if not edu_text:
        return 0.0, ["Add an Education section with your degree, institution, and graduation year."]

    score = 40.0  # base for having section
    lower = edu_text.lower()

    degree_patterns = [
        r"ph\.?d", r"master", r"m\.sc", r"m\.eng", r"mba",
        r"bachelor", r"b\.sc", r"b\.eng", r"associate", r"diploma",
    ]
    has_degree = any(re.search(p, lower) for p in degree_patterns)
    if has_degree:
        score += 30
    else:
        tips.append("Explicitly name your degree (e.g. 'Bachelor of Science in Computer Science').")

    institution_indicators = ["university", "college", "institute", "school", "polytechnic"]
    has_institution = any(ind in lower for ind in institution_indicators)
    if has_institution:
        score += 20
    else:
        tips.append("Include the name of your university or college.")

    year_re = re.compile(r"\b(19|20)\d{2}\b")
    if year_re.search(edu_text):
        score += 10
    else:
        tips.append("Include your graduation year in the Education section.")

    return min(score, 100.0), tips


def _score_projects(text: str, sections: Dict[str, str]) -> tuple[float, List[str]]:
    """Scores the projects section."""
    tips: List[str] = []
    proj_text = sections.get("projects", "")

    if not proj_text:
        tips.append(
            "Add a Projects section — it compensates for limited work experience and "
            "shows practical skills."
        )
        return 0.0, tips

    score = 40.0
    items = re.split(r"\n{2,}", proj_text.strip())
    items = [i.strip() for i in items if i.strip()]

    if len(items) >= 3:
        score += 35
    elif len(items) >= 1:
        score += 20
        tips.append("Add at least 2–3 distinct projects with descriptions and tech stacks used.")

    # Technology mentions in projects
    tech_count = sum(
        1 for kw in _ATS_KEYWORDS
        if re.search(rf"(?<!\w){re.escape(kw)}(?!\w)", proj_text.lower())
    )
    if tech_count >= 3:
        score += 25
    else:
        tips.append("Mention specific technologies used in each project (e.g. Python, React, AWS).")

    return min(score, 100.0), tips


def _score_keywords(text: str) -> tuple[float, List[str]]:
    """Checks ATS keyword density."""
    tips: List[str] = []
    lower = text.lower()
    found = [kw for kw in _ATS_KEYWORDS if re.search(rf"(?<!\w){re.escape(kw)}(?!\w)", lower)]

    ratio = len(found) / len(_ATS_KEYWORDS)
    score = min(ratio * 150, 100.0)  # generous scaling

    if score < 40:
        tips.append(
            "Include more industry-standard keywords (Python, SQL, Docker, AWS, Agile, etc.) "
            "to pass ATS filters."
        )
    elif score < 70:
        tips.append("Good keyword coverage — try to add a few more role-specific terms.")

    return score, tips


def _score_formatting(text: str) -> tuple[float, List[str]]:
    """
    Heuristic check for ATS-friendly formatting.
    Checks line length distribution and absence of table/graphics placeholders.
    """
    tips: List[str] = []
    score = 100.0

    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return 0.0, ["Resume has no detectable text structure."]

    # Check for very long lines (may indicate wall-of-text formatting)
    long_lines = [l for l in lines if len(l) > 200]
    if len(long_lines) > 5:
        score -= 25
        tips.append("Break up very long lines — ATS parsers prefer short, clear bullet points.")

    # Check for very short lines (may indicate column/table layout issues)
    tiny_lines = [l for l in lines if 0 < len(l.strip()) < 4]
    if len(tiny_lines) > 10:
        score -= 20
        tips.append(
            "Many very short fragments detected — avoid complex table/column layouts "
            "that confuse ATS parsers."
        )

    # Check word count (too short or too long)
    words = len(text.split())
    if words < 150:
        score -= 30
        tips.append("Resume content is very short — ATS may rank it low. Aim for 400–700 words.")
    elif words > 1500:
        score -= 15
        tips.append("Resume is very long — consider trimming to 1–2 pages for ATS optimisation.")

    return max(score, 0.0), tips


# ---------------------------------------------------------------------------
# Section detector (lightweight — avoids importing parse_sections)
# ---------------------------------------------------------------------------

def _quick_parse(text: str) -> Dict[str, str]:
    """
    Minimal section parser sufficient for ATS scoring.
    Returns dict of canonical section name → section text.
    """
    sections: Dict[str, str] = {
        "summary": "", "experience": "", "education": "",
        "skills": "", "projects": "", "certifications": "",
    }

    heading_map = {
        "summary": ["summary", "profile", "objective", "about me", "overview"],
        "experience": ["experience", "work experience", "employment", "professional experience"],
        "education": ["education", "academic", "qualifications", "degrees"],
        "skills": ["skills", "technical skills", "competencies", "technologies", "tools"],
        "projects": ["projects", "personal projects", "portfolio"],
        "certifications": ["certifications", "certificates", "licences", "licenses"],
    }

    current = "__pre__"
    buffer: Dict[str, List[str]] = {k: [] for k in sections}
    buffer["__pre__"] = []

    for line in text.splitlines():
        stripped = line.strip().lower().rstrip(":–—-")
        matched = None
        for canon, aliases in heading_map.items():
            if stripped in aliases or any(a in stripped for a in aliases):
                matched = canon
                break
        if matched:
            current = matched
        elif current in buffer:
            buffer[current].append(line)

    for key in sections:
        sections[key] = "\n".join(buffer.get(key, [])).strip()

    return sections


# ---------------------------------------------------------------------------
# Grade mapping
# ---------------------------------------------------------------------------

def _letter_grade(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_ats_score(text: str) -> ATSScoreResult:
    """
    Run the full ATS scoring pipeline on extracted resume text.

    Returns an ATSScoreResult with per-section scores,
    overall weighted score, missing sections, and suggestions.
    """
    sections = _quick_parse(text)

    # Score each section
    contact_score, contact_tips   = _score_contact_info(text)
    summary_score, summary_tips   = _score_summary(text, sections)
    skills_score, skills_tips     = _score_skills(text, sections)
    exp_score, exp_tips           = _score_experience(text, sections)
    edu_score, edu_tips           = _score_education(text, sections)
    proj_score, proj_tips         = _score_projects(text, sections)
    kw_score, kw_tips             = _score_keywords(text)
    fmt_score, fmt_tips           = _score_formatting(text)

    raw_scores = {
        "contact_info": round(contact_score, 1),
        "summary":      round(summary_score, 1),
        "skills":       round(skills_score, 1),
        "experience":   round(exp_score, 1),
        "education":    round(edu_score, 1),
        "projects":     round(proj_score, 1),
        "keywords":     round(kw_score, 1),
        "formatting":   round(fmt_score, 1),
    }

    # Weighted overall score
    overall = sum(raw_scores[k] * _WEIGHTS[k] for k in _WEIGHTS)
    overall = round(overall, 1)

    # Missing sections (score == 0)
    missing = [
        section.replace("_", " ").title()
        for section, score in raw_scores.items()
        if score == 0.0 and section not in ("keywords", "formatting")
    ]

    # Collect all tips
    all_tips = (
        contact_tips + summary_tips + skills_tips + exp_tips +
        edu_tips + proj_tips + kw_tips + fmt_tips
    )

    return ATSScoreResult(
        overall_score=overall,
        grade=_letter_grade(overall),
        section_scores=raw_scores,
        missing_sections=missing,
        suggestions=all_tips,
    )
