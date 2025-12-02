# =============================================================================
# Authentication Dependencies
# =============================================================================
# FastAPI dependencies for authentication, implementing the OAuth2 flow
# described in the article with JWT tokens.
# =============================================================================

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import get_user_by_username


# OAuth2 scheme - as described in the article:
# "OAuth2PasswordBearer prepares us for JWT token authentication"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Get the current user from the JWT token.

    As described in the article:
    "These functions extract the user information from the JWT token
    and verify it's valid."

    Refactored for security: Uses dependency injection for database session
    and loads SECRET_KEY from environment variables.

    Args:
        token: JWT token from Authorization header.
        db: Database session (injected).

    Returns:
        User object for the authenticated user.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Get user from database
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    token: Annotated[
        str | None,
        Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    """
    Optionally get the current user from the JWT token.

    Returns None if no token is provided or token is invalid.
    Used for public endpoints that show different content for authenticated users.
    """
    if token is None:
        return None

    try:
        payload = decode_access_token(token)
        if payload is None:
            return None

        username: str = payload.get("sub")
        if username is None:
            return None

        user = get_user_by_username(db, username=username)
        return user
    except Exception:
        return None


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current active user (not disabled).

    As described in the article:
    "The get_current_active_user function adds an extra check to make
    sure the user account isn't disabled."

    Args:
        current_user: User object from get_current_user dependency.

    Returns:
        User object if active.

    Raises:
        HTTPException: 400 if user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def convert_user_to_response(user: User) -> UserResponse:
    """
    Convert database User model to UserResponse schema.

    As described in the article's convert_db_user_to_user function:
    "Convert database user to Pydantic user model."

    Args:
        user: SQLAlchemy User model instance.

    Returns:
        UserResponse Pydantic schema.
    """
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
    )
