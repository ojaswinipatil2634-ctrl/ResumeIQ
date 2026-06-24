"""
services/analytics_service.py
-------------------------------
Analytics dashboard data aggregation.

Queries existing tables (users, resumes, ats_analyses) to produce
aggregate statistics for the dashboard endpoint.

Public API
----------
get_dashboard_stats(db: Session) -> DashboardStatsResult
"""

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.advanced import ATSAnalysis
from app.utils.skills_dict import ALL_SKILLS


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class UploadTrendItem:
    date: str   # YYYY-MM-DD
    count: int


@dataclass
class DashboardStatsResult:
    total_users: int
    total_resumes: int
    average_ats_score: Optional[float]
    most_common_skills: List[str]
    upload_trends: List[UploadTrendItem]
    top_job_titles: List[str]


# ---------------------------------------------------------------------------
# Job title extraction (re-used from analysis_service patterns)
# ---------------------------------------------------------------------------

_TITLE_KEYWORDS = [
    "engineer", "developer", "architect", "manager", "lead", "head",
    "director", "analyst", "consultant", "designer", "scientist",
    "intern", "associate", "senior", "junior", "staff", "principal",
]


def _extract_titles_from_text(text: str) -> List[str]:
    titles: List[str] = []
    for line in text.splitlines():
        lower = line.lower()
        if any(kw in lower for kw in _TITLE_KEYWORDS):
            clean = line.strip(" •·-–—\t")
            if clean and len(clean) < 80:
                titles.append(clean.lower())
    return titles[:5]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def get_dashboard_stats(db: Session) -> DashboardStatsResult:
    """
    Compute dashboard statistics by querying the database.

    Avoids heavy ORM joins — uses simple scalar queries for performance.
    """
    from app.models.user import User
    from app.models.resume import Resume

    # ── Basic counts ──────────────────────────────────────────────────────────
    total_users   = db.query(User).count()
    total_resumes = db.query(Resume).count()

    # ── Average ATS score ─────────────────────────────────────────────────────
    ats_records = db.query(ATSAnalysis.overall_score).all()
    if ats_records:
        avg_ats = round(sum(r[0] for r in ats_records) / len(ats_records), 1)
    else:
        avg_ats = None

    # ── Skill frequency across all resumes ───────────────────────────────────
    resumes = db.query(Resume.extracted_text).all()
    skill_counter: Counter = Counter()
    title_counter: Counter = Counter()

    for (text,) in resumes:
        if not text:
            continue
        normalised = text.lower()
        for skill in ALL_SKILLS:
            escaped = re.escape(skill)
            if re.search(rf"(?<!\w){escaped}(?!\w)", normalised):
                skill_counter[skill] += 1
        for title in _extract_titles_from_text(text):
            title_counter[title] += 1

    top_skills = [s for s, _ in skill_counter.most_common(10)]
    top_titles = [t for t, _ in title_counter.most_common(5)]

    # ── Upload trends (last 30 days) ──────────────────────────────────────────
    today = datetime.now(timezone.utc).date()
    trends: List[UploadTrendItem] = []

    # Build a date → count map
    date_counts: Dict[str, int] = {}
    all_uploads = db.query(Resume.uploaded_at).all()
    for (uploaded_at,) in all_uploads:
        if uploaded_at is None:
            continue
        # uploaded_at may be timezone-aware or naive depending on SQLite driver
        if hasattr(uploaded_at, "date"):
            d = uploaded_at.date()
        else:
            continue
        key = d.isoformat()
        date_counts[key] = date_counts.get(key, 0) + 1

    # Fill 30 days (0 if no uploads that day)
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        key = day.isoformat()
        trends.append(UploadTrendItem(date=key, count=date_counts.get(key, 0)))

    return DashboardStatsResult(
        total_users=total_users,
        total_resumes=total_resumes,
        average_ats_score=avg_ats,
        most_common_skills=top_skills,
        upload_trends=trends,
        top_job_titles=top_titles,
    )
