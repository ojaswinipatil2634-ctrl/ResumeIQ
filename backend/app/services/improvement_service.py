"""
services/improvement_service.py
---------------------------------
Resume improvement analysis engine.

Analyses the resume text for common weaknesses:
- Weak / missing action verbs
- Generic or vague wording
- Missing quantified achievements
- Weak project descriptions
- Missing sections

Public API
----------
generate_improvements(text: str) -> ImprovementResult
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ImprovementSection:
    area: str
    issues: List[str]
    tips: List[str]


@dataclass
class ImprovementResult:
    overall_quality: str
    sections: List[ImprovementSection]
    stronger_action_verbs: List[str]
    writing_tips: List[str]


# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

# Weak / generic verbs often found in resumes
_WEAK_VERBS = [
    "helped", "assisted", "worked on", "worked with", "responsible for",
    "involved in", "participated in", "contributed to", "tasked with",
    "supported", "handled",
]

# Strong replacements
_STRONG_VERBS = [
    "Architected", "Engineered", "Spearheaded", "Launched", "Delivered",
    "Optimised", "Automated", "Scaled", "Reduced", "Increased",
    "Led", "Mentored", "Designed", "Deployed", "Implemented",
    "Streamlined", "Migrated", "Integrated", "Built", "Drove",
    "Established", "Owned", "Shipped", "Transformed", "Accelerated",
    "Consolidated", "Revamped", "Orchestrated", "Championed", "Generated",
]

# Generic filler phrases to flag
_GENERIC_PHRASES = [
    "team player", "hard worker", "fast learner", "results-driven",
    "detail-oriented", "self-starter", "go-getter", "passionate about",
    "strong communication skills", "excellent communication",
    "outside the box", "synergy", "value-added", "proactive",
    "dynamic", "motivated individual",
]

# Quantification patterns
_METRIC_RE = re.compile(
    r"\d+\s*%|\$\s*\d+|\d+\s*[xX]\b|\d+\s*"
    r"(users?|customers?|engineers?|clients?|products?|team members?|"
    r"applications?|requests?|queries|transactions?)"
)

# Section heading quick-check
_SECTION_NAMES = {
    "summary": ["summary", "profile", "objective", "about"],
    "experience": ["experience", "work", "employment"],
    "education": ["education", "academic", "degree"],
    "skills": ["skills", "competencies", "technologies"],
    "projects": ["projects", "portfolio"],
    "certifications": ["certifications", "certificates"],
}


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_action_verbs(text: str) -> ImprovementSection:
    lower = text.lower()
    issues: List[str] = []
    tips: List[str] = []

    # Weak verbs found
    weak_found = [v for v in _WEAK_VERBS if re.search(rf"\b{re.escape(v)}\b", lower)]
    if weak_found:
        issues.append(
            f"Weak verbs detected: {', '.join(weak_found[:5])}. "
            "These are vague and fail to convey impact."
        )
        tips.append(
            "Replace weak verbs like 'helped' or 'worked on' with powerful "
            "action verbs: Built, Led, Engineered, Delivered, Optimised."
        )

    # Check for action verb at start of bullet points
    bullets = re.findall(r"^[\s•·\-–—]+(.+)", text, re.MULTILINE)
    bullets_with_weak_start = [
        b for b in bullets
        if b.strip() and not re.match(
            r"^[A-Z][a-z]+(?:ed|d|led|ped|red|ted|ned|ged|ked)\b", b.strip()
        )
    ]
    if len(bullets_with_weak_start) > len(bullets) * 0.5 and bullets:
        issues.append("Many bullet points don't start with a strong past-tense action verb.")
        tips.append(
            "Start every experience bullet with a past-tense verb: "
            "'Built a microservice that…', 'Led a team of 5 engineers…'."
        )

    if not issues:
        issues.append("Action verbs look good overall!")

    return ImprovementSection(area="Action Verbs", issues=issues, tips=tips)


def _check_generic_wording(text: str) -> ImprovementSection:
    lower = text.lower()
    issues: List[str] = []
    tips: List[str] = []

    found_generic = [p for p in _GENERIC_PHRASES if p in lower]
    if found_generic:
        issues.append(
            f"Generic phrases detected: '{', '.join(found_generic[:4])}'. "
            "These add no concrete value."
        )
        tips.append(
            "Replace generic phrases with specific evidence. Instead of 'team player', "
            "write 'Collaborated with 4 cross-functional teams to ship v2.0 on schedule'."
        )
    else:
        issues.append("No overly generic wording detected — good!")

    return ImprovementSection(area="Generic Wording", issues=issues, tips=tips)


def _check_achievements(text: str) -> ImprovementSection:
    issues: List[str] = []
    tips: List[str] = []

    metrics = _METRIC_RE.findall(text)
    metric_count = len(metrics)

    if metric_count == 0:
        issues.append("No quantified achievements found anywhere in the resume.")
        tips.append(
            "Add metrics to at least 3–5 bullet points: "
            "'Reduced API response time by 42%', 'Managed a $500k product budget', "
            "'Scaled service to 1M daily users'."
        )
        tips.append(
            "If you don't remember exact numbers, use reasonable estimates: "
            "'~30% improvement', 'team of 6 engineers'."
        )
    elif metric_count < 3:
        issues.append(f"Only {metric_count} quantified achievement(s) found — aim for at least 5.")
        tips.append(
            "Go through each bullet point and ask: 'How much? How many? How fast?' "
            "to add concrete numbers."
        )
    else:
        issues.append(f"Good — {metric_count} quantified achievements found!")

    return ImprovementSection(area="Quantified Achievements", issues=issues, tips=tips)


def _check_project_descriptions(text: str) -> ImprovementSection:
    issues: List[str] = []
    tips: List[str] = []

    # Quick section detect
    lower = text.lower()
    project_start = -1
    for marker in ["projects", "portfolio", "personal projects"]:
        idx = lower.find(marker)
        if idx != -1:
            project_start = idx
            break

    if project_start == -1:
        issues.append("No projects section detected.")
        tips.append(
            "Add 2–4 personal or professional projects with: "
            "project name, technologies used, what you built, and the outcome/impact."
        )
        return ImprovementSection(area="Project Descriptions", issues=issues, tips=tips)

    proj_text = text[project_start: project_start + 1000]
    words = len(proj_text.split())

    if words < 50:
        issues.append("Project descriptions appear very brief.")
        tips.append(
            "For each project, include: (1) what problem it solved, "
            "(2) technologies used, (3) your specific role, (4) the result or impact."
        )
    else:
        issues.append("Project section detected with sufficient content.")

    # Check for tech stack mentions in projects
    tech_markers = ["built with", "using", "stack:", "technologies:", "tech:"]
    has_tech = any(m in proj_text.lower() for m in tech_markers)
    if not has_tech:
        tips.append(
            "Explicitly list the technology stack for each project "
            "(e.g. 'Built with Python, FastAPI, PostgreSQL, deployed on AWS')."
        )

    # Check for links
    if not re.search(r"github\.com|gitlab\.com|http|www\.", proj_text, re.IGNORECASE):
        tips.append(
            "Add links to live demos or GitHub repositories for each project."
        )

    return ImprovementSection(area="Project Descriptions", issues=issues, tips=tips)


def _check_missing_sections(text: str) -> ImprovementSection:
    issues: List[str] = []
    tips: List[str] = []
    lower = text.lower()

    for section, markers in _SECTION_NAMES.items():
        if not any(m in lower for m in markers):
            issues.append(f"'{section.title()}' section appears to be missing.")
            tips.append(f"Add a clearly labelled {section.title()} section.")

    if not issues:
        issues.append("All major resume sections are present!")

    return ImprovementSection(area="Missing Sections", issues=issues, tips=tips)


def _check_length_and_structure(text: str) -> ImprovementSection:
    issues: List[str] = []
    tips: List[str] = []
    words = len(text.split())
    lines = [l for l in text.splitlines() if l.strip()]

    if words < 200:
        issues.append(f"Resume is very short ({words} words). ATS systems may rank it low.")
        tips.append("Aim for 400–700 words for a 1-page resume, 700–1200 for a 2-page resume.")
    elif words > 1200:
        issues.append(f"Resume is quite long ({words} words) — may be trimmed.")
        tips.append(
            "For most candidates (under 10 years experience), a 1-page resume is ideal. "
            "Remove older or irrelevant positions."
        )
    else:
        issues.append(f"Good length: {words} words.")

    # Blank line / whitespace check
    consecutive_blanks = sum(
        1 for i in range(len(lines) - 1)
        if not lines[i].strip() and not lines[i + 1].strip()
    )
    if consecutive_blanks > 5:
        tips.append(
            "Remove excessive blank lines — ATS parsers can misread section breaks."
        )

    return ImprovementSection(area="Length & Structure", issues=issues, tips=tips)


# ---------------------------------------------------------------------------
# Overall quality rating
# ---------------------------------------------------------------------------

def _rate_quality(text: str) -> str:
    words = len(text.split())
    metrics = len(_METRIC_RE.findall(text))
    lower = text.lower()
    sections_found = sum(
        1 for markers in _SECTION_NAMES.values()
        if any(m in lower for m in markers)
    )
    weak_found = sum(1 for v in _WEAK_VERBS if re.search(rf"\b{re.escape(v)}\b", lower))

    score = 0
    if 300 <= words <= 1200:
        score += 2
    if metrics >= 3:
        score += 3
    if sections_found >= 4:
        score += 2
    if weak_found == 0:
        score += 2
    if sections_found >= 5:
        score += 1

    if score >= 8:
        return "Excellent"
    if score >= 5:
        return "Good"
    if score >= 3:
        return "Needs Work"
    return "Poor"


# ---------------------------------------------------------------------------
# General writing tips
# ---------------------------------------------------------------------------

_WRITING_TIPS = [
    "Tailor your resume for each job by mirroring the exact keywords from the job description.",
    "Use consistent date formatting throughout (e.g. always 'Jan 2021' or always '01/2021').",
    "Put the most impressive and relevant experience first within each section.",
    "Use a clean, single-column layout with standard fonts (Arial, Calibri, or Georgia) at 10–12pt.",
    "Save your resume as a PDF unless the employer specifically requests a Word doc.",
    "Use bullet points (not paragraphs) for experience and project descriptions.",
    "Keep your email address professional — avoid nicknames or birth years.",
    "Spell-check thoroughly; grammar errors are an immediate red flag for recruiters.",
    "Include a skills section with comma-separated keywords for easy ATS parsing.",
    "List certifications and courses if you have limited work experience — they demonstrate initiative.",
]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_improvements(text: str) -> ImprovementResult:
    """
    Run the full improvement analysis pipeline on extracted resume text.
    Returns an ImprovementResult with per-area breakdowns and writing tips.
    """
    checks = [
        _check_action_verbs(text),
        _check_generic_wording(text),
        _check_achievements(text),
        _check_project_descriptions(text),
        _check_missing_sections(text),
        _check_length_and_structure(text),
    ]

    return ImprovementResult(
        overall_quality=_rate_quality(text),
        sections=checks,
        stronger_action_verbs=_STRONG_VERBS,
        writing_tips=_WRITING_TIPS,
    )
