"""
Role Service
============

This module encapsulates the business logic and database access layer for
managing user roles within the application. It provides Create and Read (CR)
operations for the ``Role`` model.

All database interactions are handled via SQLAlchemy sessions, ensuring
separation of concerns between API endpoints and data persistence logic.

Key Functions:
- ``get_role_by_id``: Retrieves a role using its primary key.
- ``get_role_by_name``: Retrieves a role using its unique name.
- ``get_all_roles``: Fetches a list of all defined roles.
- ``create_role``: Handles the creation and persistence of a new role.
"""
# =============================================================================
# Role CRUD Operations
# =============================================================================
# Database operations for Role model.
# =============================================================================

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    """
    Get role by ID.

    Args:
        db: Database session.
        role_id: The role's unique identifier.

    Returns:
        Role object if found, None otherwise.
    """
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """
    Get role by name.

    As described in the article's crud.py for checking role existence.

    Args:
        db: Database session.
        name: The role name to search for.

    Returns:
        Role object if found, None otherwise.
    """
    return db.query(Role).filter(Role.name == name).first()


def get_all_roles(db: Session) -> List[Role]:
    """
    Get all roles.

    Args:
        db: Database session.

    Returns:
        List of all Role objects.
    """
    return db.query(Role).all()


def create_role(db: Session, name: str, description: str = "") -> Role:
    """
    Create a new role.

    As described in the article's crud.py for creating roles:
    "def create_role(db: Session, name: str, description: str = ""):"

    Args:
        db: Database session.
        name: The role name.
        description: Optional role description.

    Returns:
        The created Role object.
    """
    db_role = Role(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role