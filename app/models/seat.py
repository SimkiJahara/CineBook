"""
SQLAlchemy Models for Seats and Bookings.

This module defines the models related to physical seats, the real-time status
of seats for specific shows (ShowSeat), the final confirmed booking transaction (Booking),
and the mapping of booked seats (BookedSeat).
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, ForeignKey, 
    UniqueConstraint, ForeignKeyConstraint, Numeric
)
from sqlalchemy.orm import relationship

from app.core.db import Base 
# Note: Assuming Screening model is available globally or imported in other modules
# where relationships are resolved.

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
    (Matches the ENUM type defined in CineBookSchema.sql)
    """
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

# --- Models ---

class Seat(Base):
    """
    Represents a physical seat in a screen layout.
    
    The primary key is now a composite of ``seatid`` and ``screen_id``.
    """
    __tablename__ = "seat"
    
    # FIX: Redefined Primary Key components to simplify linkage to Screen
    seatid = Column(String(50), primary_key=True) 
    screen_id = Column(Integer, ForeignKey("screen.id"), primary_key=True)
    
    # Other columns
    rownumber = Column(String(10), nullable=False)  
    number = Column(Integer, nullable=False)        
    type = Column(String(50), nullable=True)
    status = Column(String(50), default='AVAILABLE')

    # Relationships
    screen = relationship("Screen", back_populates="seats")
    show_seats = relationship("ShowSeat", back_populates="seat")

    __table_args__ = (
        # The previous ForeignKeyConstraint referencing 'seatlayout' is REMOVED to fix the error.
        # Keeping empty tuple to avoid issue with declaration of __table_args__ as non-dict
    )


class ShowSeat(Base):
    """
    Core table for real-time booking, representing the dynamic status of a seat for a specific screening.

    This model links to a :class:`Screening` and a specific :class:`Seat` via its composite primary key.
    """
    __tablename__ = "show_seat"

    id = Column(Integer, primary_key=True, index=True)
    
    # Existing FKs
    screening_id = Column(Integer, ForeignKey("screening.id"), index=True, nullable=False)
    
    # FIX: Columns for composite Foreign Key to the newly simplified Seat table
    seat_seatid = Column(String(50), nullable=False) 
    seat_screen_id = Column(Integer, nullable=False) # New FK component
    
    reserved_by_user_id = Column(Integer, ForeignKey("User.id"), nullable=True, index=True) 
    
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)
    hold_expiry_time = Column(DateTime, nullable=True) 
    
    # Relationships
    screening = relationship("Screening", back_populates="show_seats", foreign_keys=[screening_id])
    
    # FIX: Updated relationship to use the new composite key for Seat
    seat = relationship("Seat", 
                        primaryjoin="and_(ShowSeat.seat_seatid == Seat.seatid, "
                                    "ShowSeat.seat_screen_id == Seat.screen_id)",
                        foreign_keys=[seat_seatid, seat_screen_id],
                        back_populates="show_seats")
    reserved_by = relationship("User", back_populates="reserved_seats", foreign_keys="[ShowSeat.reserved_by_user_id]")


    __table_args__ = (
        # FIX: Update Composite Foreign Key Constraint to Seat table
        ForeignKeyConstraint(
            ['seat_seatid', 'seat_screen_id'],
            ['seat.seatid', 'seat.screen_id'],
            name='fk_showseat_seat'
        ),
        # FIX: Update Unique constraint to reflect the new composite key
        UniqueConstraint('screening_id', 'seat_seatid', 'seat_screen_id', name='_show_seat_uc'),
    )


class Booking(Base):
    """
    Represents a final confirmed booking transaction (e.g., ticket purchase).
    """
    __tablename__ = "booking"

    # FIX: Primary key name is 'bookingid'
    bookingid = Column(Integer, primary_key=True, index=True) 
    
    # FIX: User ID is 'buyerid' referencing 'buyer'
    buyerid = Column(Integer, ForeignKey("buyer.id"), nullable=False)
    
    # FIX: Show ID is 'screeningid' referencing 'screening'
    screeningid = Column(Integer, ForeignKey("screening.id"), nullable=False)
    
    # FIX: Column names and types match schema
    bookedat = Column(DateTime, default=datetime.utcnow, nullable=False) 
    totalamount = Column(Numeric(10,2), nullable=False) 
    paymentmethod = Column(String(50), nullable=False) 
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    
    # Additional columns from schema
    qrcodeurl = Column(String(255), nullable=True)
    promocode = Column(String(50), ForeignKey("promocode.code"), nullable=True)


    # relationships
    # 🚀 FIX: Added 'overlaps' parameter to silence the SAWarning related to User/Buyer inheritance
    user = relationship(
        "Buyer", 
        back_populates="bookings", 
        foreign_keys="[Booking.buyerid]",
        overlaps="bookings"
    )
    # FIX: Renamed 'show' to 'screening'
    screening = relationship("Screening", back_populates="bookings", foreign_keys="[Booking.screeningid]") 
    booked_seats = relationship("BookedSeat", back_populates="booking")


class BookedSeat(Base):
    """
    Mapping table between a :class:`Booking` and the individual :class:`ShowSeat` confirmed.
    """
    __tablename__ = "bookingseat" # FIX: Correct schema table name
    
    id = Column(Integer, primary_key=True, index=True) # Retaining simple PK for SQLAlchemy model ease
    
    # FIX: Foreign Key references the 'bookingid' primary key on the booking table
    booking_id = Column(Integer, ForeignKey("booking.bookingid"), nullable=False) 
    show_seat_id = Column(Integer, ForeignKey("show_seat.id"), nullable=False, unique=True)
    
    booking = relationship("Booking", back_populates="booked_seats", foreign_keys=[booking_id])
    show_seat = relationship("ShowSeat", foreign_keys=[show_seat_id])