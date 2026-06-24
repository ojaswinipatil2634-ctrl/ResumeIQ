"""
services/auth_service.py
------------------------
Pure-logic layer for auth — no FastAPI, no HTTP, no DB queries here.

Responsibilities:
- Hash and verify passwords with bcrypt via passlib
- Create signed JWT access tokens with python-jose
- Decode and validate incoming JWT tokens

Keeping this separate from routes makes it easy to unit-test
and reuse across different endpoints.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.auth import TokenData


# ── Password hashing ──────────────────────────────────────────────────────────

# bcrypt is the default scheme; deprecated="auto" lets passlib
# transparently upgrade old hashes to the current scheme on verify.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain[:72])


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*, False otherwise."""
    return _pwd_context.verify(plain[:72], hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> str:
    """
    Build and sign a JWT containing the user's id.

    Claims:
      sub  — subject (user id as string, per JWT spec)
      exp  — expiry timestamp
      iat  — issued-at timestamp
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT string.

    Raises:
        JWTError : if the token is malformed, expired, or has a bad signature.
                   Callers should catch this and raise HTTP 401.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_id_str: str | None = payload.get("sub")

    if user_id_str is None:
        raise JWTError("Token payload missing 'sub' claim")

    return TokenData(user_id=int(user_id_str))
