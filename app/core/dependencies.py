# app/core/dependencies.py

from typing import Generator
from sqlalchemy.orm import Session
# IMPORT SessionLocal from where it is defined (assuming app/database.py)
from app.core.db import SessionLocal 

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to provide a synchronous SQLAlchemy session to API endpoints.
    
    This function creates a new session per request and closes it afterward, 
    following the standard pattern for FastAPI with SQLAlchemy.
    """
    db: Session = SessionLocal()
    try:
        # The session is yielded to the endpoint function (e.g., create_new_user)
        yield db 
    finally:
        # This block runs after the response is sent
        db.close()