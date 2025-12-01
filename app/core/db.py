"""
Database Configuration and Session Management.

This module initializes the SQLAlchemy engine, defines the session factory,
and provides the Declarative Base class and a dependency function (`get_db`)
for managing database sessions within FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.core.config import settings
from typing import Generator
import os

# --- CRITICAL FIX: Conditionally skip database setup during Sphinx build ---

# Check for the SPHINX_BUILD environment variable set in conf.py
if os.environ.get('SPHINX_BUILD') != '1':

    # --- 1. Database Configuration (Actual Setup) ---
    engine = create_engine(
        settings.DATABASE_URL, 
        echo=True # Set to False in production
    )

    # --- 2. Session Local (Actual Setup) ---
    # The SessionLocal is the class used to manage sessions.
    SessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )
    
else:
    # --- 1. & 2. Database Configuration (Sphinx Mocks) ---
    # Define mock classes that satisfy the requirements of the get_db function (.rollback, .close)
    
    class MockSession:
        """Mock object for sqlalchemy.orm.Session during doc build."""
        def rollback(self): pass
        def close(self): pass
    
    def MockSessionLocal():
        """Mock factory that returns a MockSession instance."""
        return MockSession()
    
    engine = None
    SessionLocal = MockSessionLocal
    print("--- SPHINX: Database connection skipped. Using mock session. ---")


# --- 3. Base Class ---
class Base(DeclarativeBase):
    """
    The base class for all SQLAlchemy ORM models.

    All model classes in the application should inherit from this class
    to register their table metadata.
    """
    pass

# --- 4. Dependency: get_db ---

def get_db() -> Generator[Session, None, None]: # Added Session type hint
    """
    Dependency function to provide a synchronous SQLAlchemy session to API endpoints.

    This generator function yields a new database session (:class:`~sqlalchemy.orm.Session`) 
    for each request. It handles session cleanup and transaction rollback/commit
    using a try/except/finally block, ensuring resources are properly managed.

    :yield: A new SQLAlchemy :class:`~sqlalchemy.orm.Session` instance.
    :rtype: Generator[sqlalchemy.orm.Session, None, None]
    """
    db = SessionLocal() # Will be the real SessionLocal or the MockSessionLocal
    try:
        # Yield the database session to the endpoint function
        yield db
    except Exception:
        # If an error happens inside the endpoint (before db.commit()), 
        # explicitly roll back the transaction.
        db.rollback()
        raise # Re-raise the exception for FastAPI to handle
    finally:
        # Always close the session after the request is finished.
        db.close()