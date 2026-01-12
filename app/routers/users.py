# =============================================================================
# User Router
# =============================================================================
# API endpoints for user management (registration, profile, listing).
# =============================================================================

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, convert_user_to_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    get_all_users,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """
    Register a new user.

    
    "Test the registration by clicking on the /register endpoint
    and trying to register a new user"

    This endpoint creates a new user account with hashed password.
    Validates that username and email are unique.

    Args:
        user_data: UserCreate schema with registration data.
        db: Database session (injected).

    Returns:
        UserResponse with created user data (excluding password).

    Raises:
        HTTPException: 400 if username or email already exists.
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = get_user_by_email(db, email=user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create the new user
    new_user = create_user(db=db, user=user_data)

    return convert_user_to_response(new_user)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """
    Get current user information.

   
    "The /users/me endpoint shows how to get the current user's
    information using the token."

    Requires valid JWT token in Authorization header.

    Args:
        current_user: Authenticated user (injected via dependency).

    Returns:
        UserResponse with current user's data.
    """
    return convert_user_to_response(current_user)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[UserResponse]:
    """
    List all users (requires authentication).

    Returns paginated list of users. In production, you might want
    to restrict this to admin users only.

    Args:
        current_user: Authenticated user (injected via dependency).
        db: Database session (injected).
        skip: Number of records to skip (pagination offset).
        limit: Maximum number of records to return.

    Returns:
        List of UserResponse objects.
    """
    users = get_all_users(db, skip=skip, limit=limit)
    return [convert_user_to_response(user) for user in users]
