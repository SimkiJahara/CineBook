"""
SQLAlchemy Model for Movie.

This module defines the Movie table, which stores details about films available
for screening and establishes a one-to-many relationship with the Screening model.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base 

class Movie(Base):
    """
    Represents a movie available for screening.

    :ivar id: Unique primary key of the movie.
    :vartype id: int
    :ivar title: The main title of the movie (required).
    :vartype title: str
    :ivar director: The name of the movie's director.
    :vartype director: str
    :ivar release_date: The official release date of the movie.
    :vartype release_date: datetime.datetime
    :ivar duration_minutes: The runtime of the movie in minutes (required).
    :vartype duration_minutes: int
    :ivar rating: The content rating of the movie (e.g., PG, R).
    :vartype rating: str
    :ivar screenings: Relationship to the :class:`~app.models.show.Screening` model, representing
        all screenings of this movie. Deleting a movie deletes all associated screenings.
    :vartype screenings: relationship
    """

    __tablename__ = "movie"

    # FIX: This critical line must be present to resolve the 'Table already defined' error
    # caused by circular imports during application startup.
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True) 
    
    title = Column(String, nullable=False, index=True)
    director = Column(String, nullable=True)
    release_date = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    rating = Column(String, nullable=True)
    
    # Corrected target to "Screening" and relationship name to 'screenings'
    screenings = relationship(
        "Screening", 
        back_populates="movie", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"