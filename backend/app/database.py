"""Database configuration module for CineBook API.

This module sets up the SQLAlchemy engine and session for PostgreSQL
connection.
"""

from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Database session dependency for FastAPI.

    Yields a session and ensures it is closed after use.

    :yield: SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test the database connection.

    :return: True if connected successfully, False otherwise.
    """
    try:
        conn = engine.connect()
        conn.close()
        print("Database connected!")
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False


if __name__ == "__main__":
    test_connection()