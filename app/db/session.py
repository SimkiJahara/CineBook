# =============================================================================
# Database Session Configuration
# =============================================================================


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from app.core.config import get_settings


settings = get_settings()

# Create database engine
# Refactored: Removed SQLite-specific connect_args as we're using PostgreSQL
# Original article had: connect_args={"check_same_thread": False} for SQLite
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Connection pool size for production
    max_overflow=10,  # Maximum overflow connections
)
"""
SQLAlchemy :class:`~sqlalchemy.engine.Engine` instance.

This engine connects to the database specified by ``settings.database_url``
and is configured with connection pooling for performance.
"""


# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
SQLAlchemy :func:`~sqlalchemy.orm.sessionmaker` factory.

This factory is used to create new :class:`~sqlalchemy.orm.Session` objects
with specific settings (autocommit=False, autoflush=False) bound to the
application's :data:`engine`.
"""


# Base class for SQLAlchemy models
# Using the modern declarative_base import from sqlalchemy.orm
Base = declarative_base()
"""
Declarative base class for all SQLAlchemy models.

All application database models must inherit from this :class:`~sqlalchemy.ext.declarative.DeclarativeBase`.
"""


def get_db() -> Generator:
    """
    Dependency function to manage database session lifecycle for FastAPI.

    "The get_db function provides a database
    session for your endpoints." This implements proper Dependency Injection
    pattern to ensure database connections are properly managed and closed.

    :yields: A new SQLAlchemy database session instance.
    :ytype: :class:`sqlalchemy.orm.Session`
    :returns: A generator that yields a database session.
    :rtype: :class:`~typing.Generator`[:class:`~sqlalchemy.orm.Session`, None, None]

    .. note::
        The session is automatically closed in the ``finally`` block after
        the request is completed, ensuring no connection leaks occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()