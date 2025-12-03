# =============================================================================
# Database Module Initialization
# =============================================================================
"""
Public interface for the database module.

This module re-exports core components necessary for database interaction,
including the declarative base, the database engine, the session factory,
and the dependency function for session management.
"""

from app.db.session import Base, engine, SessionLocal, get_db

#: Base class for declarative models. All SQLAlchemy models should inherit from this.
Base = Base

#: SQLAlchemy Engine instance used to connect to the database.
engine = engine

#: Session factory class. Use this directly to create a new session instance.
SessionLocal = SessionLocal

#: Dependency function to yield a database session for FastAPI endpoints.
get_db = get_db

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
]