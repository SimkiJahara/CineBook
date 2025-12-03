"""
This module defines the database models related to bookings:
- Booking: Represents a user's booking for a movie screening.
- BookedSeat: Represents each individual seat reserved under a booking.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Booking(Base):
    """Booking for one screening"""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    screening_id = Column(Integer, ForeignKey("screenings.id"), nullable=False)

    total_price = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(20), nullable=False, default="PAID")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    seats = relationship(
        "BookedSeat",
        back_populates="booking",
        cascade="all, delete-orphan",
    )


class BookedSeat(Base):
    """Single seat inside a booking"""

    __tablename__ = "booked_seats"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    seat_label = Column(String(10), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    booking = relationship("Booking", back_populates="seats")
