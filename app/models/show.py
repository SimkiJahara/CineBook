"""
SQLAlchemy Model for Screening.

This module defines the Screening model (representing a specific showtime), 
which links a Movie, a Screen, and schedule details, serving as the central 
entity for booking and real-time seat status.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.db import Base 

# Explicitly import necessary models for relationships
from app.models.seat import ShowSeat, Booking 
# Assuming Movie, Screen, and User models exist and are used in other relationships

class Screening(Base): 
    """
    Represents a scheduled screening of a movie at a specific time and hall/screen.

    :ivar id: Unique primary key of the screening record.
    :vartype id: int
    :ivar movie_id: Foreign key to the :class:`~app.models.movie.Movie` being shown.
    :vartype movie_id: int
    :ivar screen_id: Foreign key to the :class:`~app.models.screen.Screen` where the movie is playing.
    :vartype screen_id: int
    :ivar start_time: The scheduled start time of the screening.
    :vartype start_time: datetime.datetime
    :ivar end_time: The calculated end time of the screening.
    :vartype end_time: datetime.datetime
    :ivar base_price: The standard ticket price for this screening.
    :vartype base_price: float
    :ivar movie: Relationship back to the parent :class:`~app.models.movie.Movie` object.
    :vartype movie: relationship
    :ivar screen: Relationship back to the parent :class:`~app.models.screen.Screen` object.
    :vartype screen: relationship
    :ivar show_seats: Relationship to the :class:`~app.models.seat.ShowSeat` model, representing
        the real-time status of all individual seats for this specific screening.
    :vartype show_seats: relationship
    :ivar bookings: Relationship to the :class:`~app.models.seat.Booking` model, listing
        all confirmed booking transactions for this screening.
    :vartype bookings: relationship
    """

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