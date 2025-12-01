"""
Core Application Dependencies.

This module defines dependency injector functions used across the FastAPI application,
primarily for managing the lifecycle of resources like database sessions.
"""

from typing import Generator
from sqlalchemy.orm import Session
# IMPORT SessionLocal from where it is defined (assuming app/database.py)
from app.core.db import SessionLocal 

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to provide a synchronous SQLAlchemy session to API endpoints.
    
    This function creates a new database session for each request. It ensures that 
    the session is always closed in the ``finally`` block, regardless of whether 
    the endpoint executed successfully or raised an exception.

    :yield: A new SQLAlchemy :class:`~sqlalchemy.orm.Session` instance.
    :rtype: Generator[sqlalchemy.orm.Session, None, None]
    """
    db: Session = SessionLocal()
    try:
        # The session is yielded to the endpoint function (e.g., create_new_user)
        yield db 
    finally:
        # This block runs after the response is sent, ensuring the session is closed
        db.close()