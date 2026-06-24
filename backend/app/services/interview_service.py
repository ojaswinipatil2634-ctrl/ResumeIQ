"""
services/interview_service.py
------------------------------
Interview question generator based on resume content.

Generates four categories of questions:
- Technical   : based on detected skills and technologies
- HR          : standard screening and culture-fit questions
- Project     : specific to projects listed on the resume
- Behavioral  : STAR-format situational questions

All logic is rule-based — no external AI API required.

Public API
----------
generate_interview_questions(text: str) -> InterviewResult
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

from app.utils.skills_dict import ALL_SKILLS, SKILLS_TAXONOMY
from app.utils.resume_parser import parse_sections


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class InterviewResult:
    technical_questions: List[str]
    hr_questions: List[str]
    project_questions: List[str]
    behavioral_questions: List[str]
    preparation_tips: List[str]


# ---------------------------------------------------------------------------
# Skill extraction helper
# ---------------------------------------------------------------------------

def _extract_skills(text: str) -> Set[str]:
    normalised = text.lower()
    found: Set[str] = set()
    for skill in ALL_SKILLS:
        escaped = re.escape(skill)
        if re.search(rf"(?<!\w){escaped}(?!\w)", normalised):
            found.add(skill)
    return found


# ---------------------------------------------------------------------------
# Technical question templates per skill category
# ---------------------------------------------------------------------------

_TECHNICAL_TEMPLATES: Dict[str, List[str]] = {
    "Programming Languages": [
        "Can you explain the difference between {} and another language you know well?",
        "What are the strengths and weaknesses of {} in a production environment?",
        "Describe a complex problem you solved using {}.",
        "What are common pitfalls or gotchas when working with {}?",
    ],
    "Web & Frontend": [
        "How does {} manage state, and what are the trade-offs of different approaches?",
        "Explain the component lifecycle in {}.",
        "How would you optimise the performance of a {} application?",
        "Describe how you would implement authentication in a {} project.",
    ],
    "Backend & APIs": [
        "How does {} handle concurrency or async operations?",
        "What is your approach to designing RESTful APIs with {}?",
        "How do you handle error propagation and logging in a {} service?",
        "Describe a scalability challenge you solved using {}.",
    ],
    "Databases": [
        "When would you choose {} over a relational/NoSQL alternative?",
        "How do you handle database migrations and schema changes in {}?",
        "Explain how indexing works in {} and when you'd add or remove an index.",
        "How would you optimise a slow query in {}?",
    ],
    "Cloud & DevOps": [
        "Walk me through how you would set up a CI/CD pipeline using {}.",
        "How do you manage secrets and environment variables in {} deployments?",
        "Describe a time you used {} to solve an infrastructure scaling problem.",
        "How do you monitor and alert on services deployed with {}?",
    ],
    "Data & ML": [
        "Explain the end-to-end workflow you use for a {} project.",
        "How do you evaluate and avoid overfitting in a {} model?",
        "Describe how you would prepare a messy dataset for training using {}.",
        "What metrics do you use to measure model performance in a {} project?",
    ],
    "Testing & QA": [
        "How do you decide what to unit-test vs. integration-test in a {} workflow?",
        "Describe your approach to writing maintainable tests with {}.",
        "How do you handle flaky tests, and how has {} helped you with this?",
    ],
    "Tools & Practices": [
        "Describe your {} workflow on a team of 5+ engineers.",
        "How do you use {} to manage releases and hotfixes?",
        "What does a healthy {} process look like on a fast-moving team?",
    ],
}

# Generic technical questions (always included)
_GENERIC_TECHNICAL = [
    "How do you approach debugging a production issue you've never seen before?",
    "Describe the most technically complex project you've worked on.",
    "How do you stay current with new technologies and industry trends?",
    "Walk me through how you would design a URL shortener (or a simple distributed system).",
    "How do you balance technical debt against feature delivery?",
    "What does 'clean code' mean to you, and how do you enforce it on a team?",
]


# ---------------------------------------------------------------------------
# HR questions
# ---------------------------------------------------------------------------

_HR_QUESTIONS = [
    "Tell me about yourself and your career journey so far.",
    "Why are you interested in this role and our company?",
    "Where do you see yourself in 3–5 years?",
    "What is your greatest professional strength, and can you give an example?",
    "What is an area you are actively working to improve?",
    "How do you handle tight deadlines or multiple competing priorities?",
    "Describe your ideal working environment.",
    "What motivates you to do your best work?",
    "How do you prefer to receive feedback?",
    "What salary range are you targeting, and what factors matter most to you beyond salary?",
    "Do you have any questions for us about the team, role, or culture?",
    "Are you currently interviewing elsewhere? What is your timeline?",
]


# ---------------------------------------------------------------------------
# Behavioral questions (STAR format)
# ---------------------------------------------------------------------------

_BEHAVIORAL_QUESTIONS = [
    "Tell me about a time you had to deliver a project under a very tight deadline. What did you do?",
    "Describe a situation where you disagreed with a teammate or manager. How did you resolve it?",
    "Give an example of a time you identified and fixed a significant bug or performance issue.",
    "Tell me about a project that failed or did not go as planned. What did you learn?",
    "Describe a time you had to learn a new technology quickly. How did you approach it?",
    "Give an example of when you went above and beyond your core responsibilities.",
    "Tell me about a time you mentored or helped a junior colleague grow.",
    "Describe a situation where you had to make a technical decision with incomplete information.",
    "Give an example of a time you improved a process or workflow on your team.",
    "Tell me about the most impactful piece of feedback you have received.",
]


# ---------------------------------------------------------------------------
# Project question builder
# ---------------------------------------------------------------------------

def _build_project_questions(text: str, sections: Dict[str, str]) -> List[str]:
    """Generate questions specific to projects listed on the resume."""
    questions: List[str] = []
    proj_text = sections.get("projects", "")

    if not proj_text:
        # Fall back to generic project questions
        return [
            "Can you describe a personal or side project you are proud of?",
            "What is a project where you built something end-to-end by yourself?",
            "Have you contributed to any open-source projects? Tell me about it.",
            "Describe a project where you had to pick a tech stack from scratch — what did you choose and why?",
        ]

    # Try to extract project names (capitalized phrases before a colon or newline)
    project_names = re.findall(r"^([A-Z][A-Za-z0-9\s\-]+?)(?:\s*[-–:|\n])", proj_text, re.MULTILINE)
    project_names = [n.strip() for n in project_names if 2 < len(n.strip()) < 50][:4]

    generic_project_qs = [
        "Walk me through the architecture of {} — what were the key design decisions?",
        "What was the hardest technical challenge you faced while building {}?",
        "If you had to rebuild {} from scratch today, what would you do differently?",
        "How did you test and validate {} before releasing it?",
        "What would the next feature or improvement be for {}?",
    ]

    for name in project_names:
        q_template = generic_project_qs[len(questions) % len(generic_project_qs)]
        questions.append(q_template.format(name))

    # Always add some generic project questions
    questions += [
        "Which project on your resume are you most proud of, and why?",
        "How did you decide on the technology stack for your main project?",
        "Did any of your projects involve collaborating with other developers? How did you coordinate?",
    ]

    return questions[:8]  # cap at 8


# ---------------------------------------------------------------------------
# Technical question builder
# ---------------------------------------------------------------------------

def _build_technical_questions(skills: Set[str]) -> List[str]:
    """Build skill-specific technical questions."""
    questions: List[str] = []

    for category, templates in _TECHNICAL_TEMPLATES.items():
        cat_skills = [s for s in SKILLS_TAXONOMY.get(category, []) if s in skills]
        if not cat_skills:
            continue
        # Pick the top 2 skills in this category and generate 2 questions each
        for skill in cat_skills[:2]:
            for template in templates[:2]:
                questions.append(template.format(skill.title()))

    # Always include generic technical questions
    questions.extend(_GENERIC_TECHNICAL)

    # Deduplicate and limit
    seen: Set[str] = set()
    unique: List[str] = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    return unique[:15]


# ---------------------------------------------------------------------------
# Preparation tips
# ---------------------------------------------------------------------------

_PREP_TIPS = [
    "Research the company's products, culture, and recent news before the interview.",
    "Prepare 3–5 STAR stories (Situation, Task, Action, Result) covering different skills.",
    "Review every item on your resume — be ready to discuss any project or technology in depth.",
    "Practice coding challenges on LeetCode or HackerRank, focusing on arrays, trees, and graphs.",
    "Prepare 3–5 thoughtful questions to ask the interviewer about the team and role.",
    "Do a mock interview with a friend or use a tool like Pramp or interviewing.io.",
    "Arrive (or log in) a few minutes early and test your audio/video for remote interviews.",
    "Write down the key highlights you want the interviewer to remember about you.",
    "Follow up with a thank-you email within 24 hours of the interview.",
    "Know your expected salary range and be prepared to discuss it professionally.",
]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_interview_questions(text: str) -> InterviewResult:
    """
    Generate interview questions tailored to the resume content.

    Steps:
    1. Parse resume into sections.
    2. Extract detected skills.
    3. Build skill-specific technical questions.
    4. Build project-specific questions.
    5. Return standard HR and behavioral questions.
    """
    sections = parse_sections(text)
    skills = _extract_skills(text)

    technical = _build_technical_questions(skills)
    project   = _build_project_questions(text, sections)

    return InterviewResult(
        technical_questions=technical,
        hr_questions=_HR_QUESTIONS,
        project_questions=project,
        behavioral_questions=_BEHAVIORAL_QUESTIONS,
        preparation_tips=_PREP_TIPS,
    )
