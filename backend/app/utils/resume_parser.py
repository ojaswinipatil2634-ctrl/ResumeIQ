"""
utils/resume_parser.py
-----------------------
Splits raw resume text into logical sections (Experience, Education,
Skills, Summary, etc.) using heading-detection heuristics.

No ML, no external APIs — just regex pattern matching and line-by-line
scanning. Deterministic and fast (~1 ms for a typical resume).

Public API
----------
parse_sections(text: str) -> dict[str, str]
    Returns a mapping of canonical section name → section text.
    Always returns the same keys (some values may be empty strings).
"""

import re
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Section heading patterns
# Each entry is (canonical_name, [alias_patterns…])
# Patterns are matched case-insensitively against a stripped line.
# ---------------------------------------------------------------------------
_SECTION_ALIASES: List[Tuple[str, List[str]]] = [
    ("summary", [
        r"summary", r"profile", r"objective", r"about me",
        r"professional summary", r"career objective", r"overview",
    ]),
    ("experience", [
        r"experience", r"work experience", r"employment",
        r"professional experience", r"work history", r"career history",
        r"positions? held",
    ]),
    ("education", [
        r"education", r"academic", r"qualifications?",
        r"educational background", r"degrees?",
    ]),
    ("skills", [
        r"skills?", r"technical skills?", r"core competencies",
        r"competencies", r"technologies", r"tools",
    ]),
    ("projects", [
        r"projects?", r"personal projects?", r"side projects?",
        r"portfolio",
    ]),
    ("certifications", [
        r"certifications?", r"certificates?", r"licen[sc]es?",
        r"accreditations?",
    ]),
    ("languages", [
        r"languages?", r"spoken languages?", r"language proficiency",
    ]),
    ("interests", [
        r"interests?", r"hobbies", r"activities", r"volunteering",
    ]),
]

# Pre-compile: (canonical_name, compiled_pattern)
_COMPILED: List[Tuple[str, re.Pattern]] = [
    (
        canon,
        re.compile(
            r"^(?:" + "|".join(aliases) + r")\s*[:\-–—]?\s*$",
            re.IGNORECASE,
        ),
    )
    for canon, aliases in _SECTION_ALIASES
]


def _detect_heading(line: str) -> str | None:
    """
    Return the canonical section name if *line* looks like a heading,
    else None.

    A line is considered a heading if:
      - It matches one of the known section alias patterns, OR
      - It is SHORT (≤ 40 chars), ALL-CAPS or Title-Case, and
        doesn't look like a sentence (no verb-like punctuation).
    """
    stripped = line.strip()
    if not stripped:
        return None

    # 1. Exact alias match
    for canon, pattern in _COMPILED:
        if pattern.match(stripped):
            return canon

    # 2. Heuristic: short ALL-CAPS line
    if len(stripped) <= 40 and stripped.isupper() and len(stripped.split()) <= 5:
        # Map to a known section if possible
        lower = stripped.lower()
        for canon, aliases in _SECTION_ALIASES:
            for alias in aliases:
                if re.search(alias, lower):
                    return canon
        return f"__custom__{stripped.title()}"

    return None


def parse_sections(text: str) -> Dict[str, str]:
    """
    Parse *text* into sections.

    Returns a dict with keys:
        summary, experience, education, skills,
        projects, certifications, languages, interests, __preamble__

    Values are stripped strings; empty string means section not found.
    """
    result: Dict[str, str] = {
        "__preamble__": "",
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "languages": "",
        "interests": "",
    }

    lines = text.splitlines()
    current_section = "__preamble__"
    buffer: List[str] = []

    def _flush():
        result[current_section] = (result.get(current_section, "") + "\n".join(buffer)).strip()
        buffer.clear()

    for line in lines:
        heading = _detect_heading(line)
        if heading and heading in result:
            _flush()
            current_section = heading
        else:
            buffer.append(line)

    _flush()
    return result
