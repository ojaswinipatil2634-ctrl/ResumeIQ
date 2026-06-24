"""
api/auth.py
-----------
Auth routes: register, login, and the protected /me endpoint.

All routes live under the /api/auth prefix (set in main.py).

Design notes:
- DB queries stay in the route; for a larger codebase move them
  to a UserRepository / CRUD layer.
- Passwords are NEVER stored or returned in plain text.
- On success, both /register and /login return the same Token shape
  so the frontend can handle both responses identically.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut
from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["Auth"])


# ── POST /api/auth/register ───────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    """
    Create a new account.

    - Rejects duplicate emails with **409 Conflict**.
    - Returns a JWT so the user is immediately logged in after sign-up.
    """
    # 1. Check for duplicate email
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # 2. Persist new user (password is hashed, never stored plain)
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 3. Issue JWT and return
    return Token(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


# ── POST /api/auth/login ──────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=Token,
    summary="Log in and receive a JWT",
)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    """
    Authenticate with email + password.

    - Returns **401** for wrong email *or* wrong password
      (same message intentionally — avoids leaking which one failed).
    """
    _invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Look up user
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        raise _invalid

    # 2. Verify password
    if not verify_password(payload.password, user.hashed_password):
        raise _invalid

    # 3. Check account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return Token(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


# ── GET /api/auth/me ──────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the currently authenticated user",
)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """
    Protected route — requires a valid Bearer token.

    The `get_current_user` dependency (injected by FastAPI) handles
    all token validation. If the token is missing, expired, or invalid,
    FastAPI automatically returns **401** before this function runs.
    """
    return UserOut.model_validate(current_user)
