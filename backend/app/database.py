from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.settings import settings


# Load DATABASE_URL from .env
DATABASE_URL = settings.DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Provide a database session to routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def init_db():
    """
    Create all database tables based on the SQLAlchemy models.
    Call this once when the app starts.
    """
    # Import models so that SQLAlchemy knows them
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

