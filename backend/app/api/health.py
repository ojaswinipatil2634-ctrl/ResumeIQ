"""
api/health.py
-------------
Health check endpoints.
Used to verify the server is running and the DB connection is alive.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    """
    Basic liveness check.
    Returns app name, version, and status.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/db", tags=["Health"])
def db_health_check(db: Session = Depends(get_db)):
    """
    Database connectivity check.
    Runs a simple SELECT 1 query to confirm the DB is reachable.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
