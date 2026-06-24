"""
schemas/auth.py
---------------
Pydantic v2 schemas for auth request bodies and responses.

Separation of concerns:
- UserCreate    : what the client sends to /register
- UserLogin     : what the client sends to /login
- UserOut       : what we safely return to the client (NO password)
- Token         : the JWT envelope returned after login/register
- TokenData     : the payload we encode inside the JWT
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ── Inbound ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Registration request body."""
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    full_name: str | None = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    """Login request body."""
    email: EmailStr
    password: str


# ── Outbound ──────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    """Safe user representation — never exposes hashed_password."""
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}   # replaces orm_mode in Pydantic v2


class Token(BaseModel):
    """JWT response returned after successful login or registration."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── JWT payload ───────────────────────────────────────────────────────────────

class TokenData(BaseModel):
    """Data encoded inside the JWT (the 'sub' claim)."""
    user_id: int
