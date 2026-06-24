"""
core/dependencies.py
--------------------
Reusable FastAPI dependencies.

get_current_user
    Extracts the Bearer token from the Authorization header,
    decodes it, looks up the user in the DB, and returns the
    User ORM object.

    Inject it into any route that requires authentication:

        @router.get("/protected")
        def protected(current_user: User = Depends(get_current_user)):
            return {"hello": current_user.email}

    FastAPI automatically returns HTTP 401 if the dependency raises
    HTTPException, so callers never have to handle auth manually.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token

# Tells FastAPI where clients send their token (used by Swagger UI too)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: decode JWT → fetch user → return User ORM object.
    Raises HTTP 401 on any failure (bad token, expired, user not found).
    """
    try:
        token_data = decode_access_token(token)
    except JWTError:
        raise _401

    user = db.get(User, token_data.user_id)
    if user is None:
        raise _401
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user
