from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.core.config import settings
from typing import Generator

# --- 1. Database Configuration ---

# **Optimized for PostgreSQL/Server Databases:**
# Removed conditional logic and the SQLite-specific 'connect_args'.
# The standard create_engine call is sufficient for server-based databases.
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True # Set to False in production
)


# --- 2. Session Local ---
# The SessionLocal is the class used to manage sessions.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# --- 3. Base Class ---
class Base(DeclarativeBase):
    pass

# --- 4. Dependency: get_db ---

def get_db() -> Generator[Session, None, None]: # Added Session type hint
    """
    Dependency function to provide a synchronous SQLAlchemy session to API endpoints.
    Uses a try/except/finally block to ensure connection is closed and 
    rollback is performed on any error, otherwise commits are kept.
    """
    db = SessionLocal()
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