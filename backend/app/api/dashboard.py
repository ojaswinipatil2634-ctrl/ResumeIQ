"""
api/dashboard.py
----------------
Analytics dashboard endpoint.

GET /api/dashboard/stats
    - Requires authentication (Bearer token)
    - Aggregates statistics from users, resumes, and ats_analyses tables
    - Returns total counts, average ATS score, top skills, upload trends,
      and top job titles

Intended for admin dashboards or personal analytics views.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.advanced import DashboardStats, UploadTrend
from app.services.analytics_service import get_dashboard_stats

router = APIRouter(tags=["Analytics Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get aggregated analytics dashboard statistics",
    description=(
        "Returns platform-wide statistics: total users, total resumes, "
        "average ATS score (across all scored resumes), most common skills "
        "found across all resumes, upload trends for the last 30 days, "
        "and most frequently detected job titles."
    ),
)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardStats:
    """
    Aggregate and return analytics statistics.

    Requires authentication so anonymous users can't see platform stats.
    """
    result = get_dashboard_stats(db)

    return DashboardStats(
        total_users=result.total_users,
        total_resumes=result.total_resumes,
        average_ats_score=result.average_ats_score,
        most_common_skills=result.most_common_skills,
        upload_trends=[
            UploadTrend(date=t.date, count=t.count)
            for t in result.upload_trends
        ],
        top_job_titles=result.top_job_titles,
    )
