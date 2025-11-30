# /app/models/show.py (Final Fixed Code)

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.db import Base 

# Explicitly import necessary models for relationships
# If these models are not defined in the same file, they MUST be imported
from app.models.seat import ShowSeat, Booking 
# Assuming Movie, Screen, and User models exist and are used in other relationships

class Screening(Base): 
    """Represents a scheduled screening of a movie at a specific time and hall/screen."""

    __tablename__ = "screening" 

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    movie_id = Column(Integer, ForeignKey("movie.id"), index=True, nullable=False) 
    screen_id = Column(Integer, ForeignKey("screen.id"), index=True, nullable=False) 
    
    # Show details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    base_price = Column(Float, nullable=False)
    
    # Relationships
    movie = relationship("Movie", back_populates="screenings") 
    screen = relationship("Screen", back_populates="screenings") 
    
    # Relationship to ShowSeat
    show_seats = relationship(
        "ShowSeat", 
        back_populates="screening", 
        cascade="all, delete-orphan",
        foreign_keys="[ShowSeat.screening_id]" # Added foreign_keys argument
    )
    
    # Relationship to Booking
    bookings = relationship("Booking", back_populates="screening") 

    def __repr__(self):
        return f"<Screening(id={self.id}, start_time='{self.start_time}')>"