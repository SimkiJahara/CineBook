# app/models/booking.py

"""
Database models for ticket bookings.

Booking:
    One row per ticket order.
    Example: user books 3 seats for one screening.

BookedSeat:
    One row per seat inside a booking.
    Example: seats A1, A2, A3 = 3 rows in this table.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Booking(Base):
    """
    Booking table.

    One booking is:
    - one user
    - one screening
    - many seats
    """

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # For now, we just store user as an integer.
    # Later you can connect this to a real User table.
    user_id = Column(Integer, nullable=False)

    # Link to a screening (from your Screening model)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False)

    # Simple payment info
    total_price = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # e.g. "bkash", "nagad", "card"
    payment_status = Column(String(20), nullable=False, default="PAID")

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship to BookedSeat
    seats = relationship("BookedSeat", back_populates="booking", cascade="all, delete-orphan")


class BookedSeat(Base):
    """
    Seats inside a booking.

    Each row = one seat (like 'A1', 'A2').
    """

    __tablename__ = "booked_seats"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    # seat label like "A1", "B5"
    seat_label = Column(String(10), nullable=False)

    # price for this seat (you can copy from screening base_price, or add extra logic later)
    price = Column(Numeric(10, 2), nullable=False)

    # back reference to Booking
    booking = relationship("Booking", back_populates="seats")
