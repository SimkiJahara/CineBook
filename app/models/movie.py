# /app/models/movie.py (Final Verified Code)

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base 

class Movie(Base):
    """Represents a movie available for screening."""

    __tablename__ = "movie"

    # CRITICAL FIX: Ensure primary_key=True is present and correctly capitalized
    id = Column(Integer, primary_key=True, index=True) 
    
    title = Column(String, nullable=False, index=True)
    director = Column(String, nullable=True)
    release_date = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    rating = Column(String, nullable=True)
    
    # Relationships back to the Show model
    shows = relationship(
        "Show", 
        back_populates="movie", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"