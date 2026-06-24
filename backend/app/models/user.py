"""
models/user.py
--------------
SQLAlchemy ORM model for the users table.

Columns:
- id            : auto-incrementing primary key
- email         : unique, indexed — used as login identifier
- hashed_password : bcrypt hash, never store plaintext
- full_name     : optional display name
- is_active     : soft-disable accounts without deleting them
- created_at    : UTC timestamp set on insert
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
