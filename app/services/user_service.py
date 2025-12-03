"""
User Service
============

This module contains the core business logic and database access functions for
managing user accounts, handling authentication, and updating user profiles.
It ensures that sensitive operations, like password hashing, are properly
isolated in the service layer.

Key Functions:
- **User Retrieval**: ``get_user_by_id``, ``get_user_by_username``, ``get_user_by_email``, ``get_all_users``.
- **Authentication**: ``authenticate_user`` verifies credentials against the stored hash.
- **Creation/Update**: ``create_user`` handles registration and default role assignment; ``update_user_status`` manages account activation/deactivation.
"""
# =============================================================================
# User CRUD Operations
# =============================================================================
# Database operations for User model, adapted from the article's crud.py.
# All functions include proper type hints and docstrings.
# =============================================================================

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get user by ID.

    As described in the article's crud.py: retrieves a user by their unique ID.

    Args:
        db: Database session.
        user_id: The user's unique identifier.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get user by username.

    As described in the article: "get_user finds a user in the database"
    Used for authentication and uniqueness checks.

    Args:
        db: Database session.
        username: The username to search for.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email.

    Used for checking email uniqueness during registration.

    Args:
        db: Database session.
        email: The email to search for.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Get all users with pagination.

    As described in the article's crud.py for listing users.

    Args:
        db: Database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        List of User objects.
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    As described in the article's crud.py:
    "hashed_password = pwd_context.hash(user.password)"
    Passwords are always hashed before storage.

    Args:
        db: Database session.
        user: UserCreate schema with registration data.

    Returns:
        The created User object.
    """
    # Hash the password - NEVER store plain text
    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
    )

    # Assign default 'user' role if it exists
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password.

    As described in the article:
    "authenticate_user checks if the provided username and password
    are correct by verifying the hashed password."

    Args:
        db: Database session.
        username: The username to authenticate.
        password: The plain text password to verify.

    Returns:
        User object if authentication successful, None otherwise.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_status(db: Session, user_id: int, is_active: bool) -> Optional[User]:
    """
    Update user active status.

    Used for enabling/disabling user accounts.

    Args:
        db: Database session.
        user_id: The user's unique identifier.
        is_active: The new active status.

    Returns:
        Updated User object if found, None otherwise.
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.is_active = is_active
        db.commit()
        db.refresh(user)
    return user