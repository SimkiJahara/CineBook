# /app/models/seat.py (Final Verified Code)

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base 

# --- Enums ---

class SeatStatus(enum.Enum):
    """
    Status of a seat for a specific show.
    """
    AVAILABLE = "Available"
    PENDING = "Pending"
    BOOKED = "Booked"

class BookingStatus(enum.Enum):
    """
    Status of a final booking transaction.
    """
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

# --- Models ---

class Seat(Base):
    """
    Represents a physical seat (the table referenced by show_seat.seat_id).
    """
    __tablename__ = "seat"
    
    # CRITICAL FIX: The ID column must be explicitly marked as primary_key=True
    id = Column(Integer, primary_key=True, index=True) 
    
    # Foreign Key linking to the Screen table (which has its own simple id)
    screen_id = Column(Integer, ForeignKey("screen.id"), nullable=False)
    
    seat_number = Column(String, index=True) 
    row_number = Column(String, index=True)  

    # Relationships
    screen = relationship("Screen", back_populates="seats")
    show_seats = relationship("ShowSeat", back_populates="seat")

    __table_args__ = (
        UniqueConstraint('screen_id', 'seat_number', 'row_number', name='_physical_seat_uc'),
    )


class ShowSeat(Base):
    """
    Core table for real-time booking.
    """
    __tablename__ = "show_seat"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys 
    show_id = Column(Integer, ForeignKey("show.id"), index=True, nullable=False)
    seat_id = Column(Integer, ForeignKey("seat.id"), index=True, nullable=False) 
    reserved_by_user_id = Column(Integer, ForeignKey("User.id"), nullable=True, index=True) # References "User" (Capital U)
    
    # Core Booking Status Columns (Two-Phase Commit)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)
    hold_expiry_time = Column(DateTime, nullable=True) 
    
    # Relationships
    show = relationship("Show", back_populates="show_seats")
    seat = relationship("Seat", back_populates="show_seats")
    reserved_by = relationship("User", back_populates="reserved_seats", foreign_keys="[ShowSeat.reserved_by_user_id]")


    __table_args__ = (
        UniqueConstraint('show_id', 'seat_id', name='_show_seat_uc'),
    )


class Booking(Base):
    """Represents a final confirmed booking transaction."""
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    show_id = Column(Integer, ForeignKey("show.id"), nullable=False)
    booking_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_price = Column(Integer, nullable=False)
    payment_token = Column(String, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)

    # relationships
    user = relationship("User", back_populates="bookings", foreign_keys="[Booking.user_id]")
    show = relationship("Show", back_populates="bookings")
    booked_seats = relationship("BookedSeat", back_populates="booking")


class BookedSeat(Base):
    """Mapping table between a Booking and the individual seats confirmed."""
    __tablename__ = "booked_seat"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("booking.id"), nullable=False)
    show_seat_id = Column(Integer, ForeignKey("show_seat.id"), nullable=False, unique=True)
    
    booking = relationship("Booking", back_populates="booked_seats")
    show_seat = relationship("ShowSeat")