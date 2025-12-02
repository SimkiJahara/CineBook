# =============================================================================
# Database Session Configuration
# =============================================================================
# Refactored for security: Database URL is loaded from environment variables
# instead of being hardcoded as in the original article.
#
# The article used: DATABASE_URL = "sqlite:///./auth.db" (hardcoded)
# We now use: settings.database_url (from .env file)
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

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
# Using the modern declarative_base import from sqlalchemy.orm
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency to get database session.

    As described in the article: "The get_db function provides a database
    session for your endpoints." This implements proper Dependency Injection
    pattern to ensure database connections are properly managed and closed.

    Yields:
        Session: SQLAlchemy database session.

    Note:
        The session is automatically closed after the request is completed,
        ensuring no connection leaks occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
