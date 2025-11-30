# /app/models/show.py (Modified to link back to Movie)

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.db import Base 

class Show(Base):
    """Represents a scheduled screening of a movie at a specific time and screen."""

    __tablename__ = "show"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    movie_id = Column(Integer, ForeignKey("movie.id"), index=True, nullable=False) # References 'movie' table
    screen_id = Column(Integer, ForeignKey("screen.id"), index=True, nullable=False) 
    
    # Show details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    base_price = Column(Float, nullable=False)
    
    # Relationships
    movie = relationship("Movie", back_populates="shows")
    screen = relationship("Screen", back_populates="shows")
    show_seats = relationship(
        "ShowSeat", 
        back_populates="show", 
        cascade="all, delete-orphan",
    )
    bookings = relationship("Booking", back_populates="show")

    def __repr__(self):
        return f"<Show(id={self.id}, start_time='{self.start_time}')>"