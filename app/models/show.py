"""
SQLAlchemy Models for Screening.

This module defines the Screening table and imports necessary dependencies.
"""

from datetime import datetime
# Importing Float and ForeignKey are necessary for the columns defined below
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.db import Base 
# Note: You may need to import Movie and Screen if your IDE/linter complains, 
# but SQLAlchemy can resolve the strings if the models are imported in main.py.
# from .movie import Movie
# from .screen import Screen 

class Screening(Base):
    """
    Represents a specific showing of a movie at a theatre screen.
    """
    __tablename__ = "screening"
    
    # FIX 1: Add extend_existing=True for robustness, as models are imported in main.py
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True) 
    
    # --- Foreign Keys ---
    movie_id = Column(Integer, ForeignKey("movie.id"), index=True, nullable=False)
    
    # 💡 FIX 2: Add the foreign key column linking a screening to its screen.
    screen_id = Column(Integer, ForeignKey("screen.id"), index=True, nullable=False)
    
    start_time = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)

    # --- Relationships ---
    # 1. Relationship back to Movie
    movie = relationship("Movie", back_populates="screenings")

    # 2. FIX 3: Relationship back to Screen to satisfy the Screen.screenings relationship
    screen = relationship("Screen", back_populates="screenings")

    # 3. Relationship to ShowSeat (Defined in app/models/seat.py with back_populates="screening")
    show_seats = relationship(
        "ShowSeat", 
        back_populates="screening",
        cascade="all, delete-orphan", 
        primaryjoin="Screening.id == ShowSeat.screening_id" 
    )
    
    # 4. Relationship to Booking (Defined in app/models/seat.py with back_populates="screening")
    bookings = relationship("Booking", back_populates="screening")
    
    def __repr__(self):
        return f"<Screening(id={self.id}, movie_id={self.movie_id}, screen_id={self.screen_id}, start_time='{self.start_time}')>"