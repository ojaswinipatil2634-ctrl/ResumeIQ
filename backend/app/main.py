"""
app/main.py  (Part 5 — updated)
--------------------------------
FastAPI application entry point.

Changes from Part 4:
- Imports all new Part 5 models so SQLAlchemy creates their tables on startup.
- Registers the five new Part 5 routers (ATS, Job Match, Improvement,
  Interview, Roadmap) and the Analytics Dashboard router.

All previously registered routers (health, auth, resume, analysis)
are preserved unchanged.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.api import health
from app.api import auth
from app.api import resume
from app.api import analysis

# ── Part 5 routers ────────────────────────────────────────────────────────────
from app.api import ats
from app.api import job_match
from app.api import improvement
from app.api import interview
from app.api import roadmap
from app.api import dashboard

# ── Model imports (ensures tables are created by create_all) ──────────────────
from app.models import user as _user_model         # noqa: F401
from app.models import resume as _resume_model     # noqa: F401
from app.models import advanced as _advanced_model # noqa: F401  ← Part 5 models


def create_app() -> FastAPI:
    """
    Application factory — builds and configures the FastAPI app.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "## ResumeIQ — AI-powered Resume Analyzer API\n\n"
            "### Feature Overview\n"
            "- **Auth** : register, login, JWT-protected routes\n"
            "- **Resume** : upload PDF/DOCX, extract text\n"
            "- **Analysis** : skills, experience, education insights\n"
            "- **ATS Scoring** : ATS score with section breakdown\n"
            "- **Job Matching** : match resume against a job description\n"
            "- **Improvement** : actionable resume writing suggestions\n"
            "- **Interview Prep** : personalised interview questions\n"
            "- **Career Roadmap** : technologies, certs, and learning plan\n"
            "- **Dashboard** : platform analytics statistics\n"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Database ──────────────────────────────────────────────────────────────
    # Creates all tables (including Part 5's new tables) if they don't exist.
    Base.metadata.create_all(bind=engine)

    # ── Routers — Parts 1–4 (unchanged) ──────────────────────────────────────
    app.include_router(health.router,   prefix="/api/v1")
    app.include_router(auth.router,     prefix="/api/auth")
    app.include_router(resume.router,   prefix="/api/resume")
    app.include_router(analysis.router, prefix="/api/analysis")

    # ── Routers — Part 5 (new) ────────────────────────────────────────────────
    app.include_router(ats.router,         prefix="/api/ats")
    app.include_router(job_match.router,   prefix="/api/job-match")
    app.include_router(improvement.router, prefix="/api/improve")
    app.include_router(interview.router,   prefix="/api/interview")
    app.include_router(roadmap.router,     prefix="/api/roadmap")
    app.include_router(dashboard.router,   prefix="/api/dashboard")

    return app


app = create_app()
