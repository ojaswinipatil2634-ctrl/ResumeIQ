"""
db/database.py
--------------
Sets up the SQLAlchemy engine, session factory, and Base class.

Key concepts:
- engine       : the actual connection to the SQLite file
- SessionLocal : a factory that creates DB sessions (one per request)
- Base         : all ORM models inherit from this
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# connect_args is required for SQLite to allow multi-threaded access
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Each request gets its own session; autocommit/autoflush are OFF
# so we control when data is committed
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """All ORM models inherit from this Base."""
    pass


def get_db():
    """
    FastAPI dependency — yields a DB session per request,
    then closes it automatically when the request is done.

    Usage in a route:
        @router.get("/something")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
