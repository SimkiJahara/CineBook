"""
This module initializes database connection and session handling

It provides:
- get_db(): starts a DB session to FastAPI routes
- init_db(): initializes database tables on startup
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.settings import settings


# Database Configuration

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# Get the  DB Session

def get_db():
    """Provides a database session for FastAPI requests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database Initialization

def init_db():
    """Initialize database tables"""
    from app import models  
    Base.metadata.create_all(bind=engine)
