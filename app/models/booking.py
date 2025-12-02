# =============================================================================
# Booking Models - Seat and Booking SQLAlchemy Models
# =============================================================================
# Database models for the movie ticket booking system.
# Includes Seat (theater layout) and Booking (user reservations).
# =============================================================================

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class SeatType(str, enum.Enum):
    """Seat type enumeration for pricing tiers."""

    STANDARD = "standard"
    VIP = "vip"


class Seat(Base):
    """
    Seat model representing a single seat in the theater.

    Attributes:
        id: Primary key
        row: Row identifier (e.g., 'A', 'B', 'C')
        number: Seat number within the row (1, 2, 3...)
        seat_type: Type of seat (standard/vip) for pricing
        price: Price in Taka
    """

    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    row = Column(String(2), nullable=False)
    number = Column(Integer, nullable=False)
    seat_type = Column(String(20), nullable=False, default=SeatType.STANDARD.value)
    price = Column(Float, nullable=False, default=10.0)

    # Relationship to booking
    booking = relationship("Booking", back_populates="seat", uselist=False)

    # Ensure unique seat positions
    __table_args__ = (UniqueConstraint("row", "number", name="unique_seat_position"),)

    def __repr__(self) -> str:
        return f"<Seat {self.row}{self.number} ({self.seat_type})>"


class Booking(Base):
    """
    Booking model representing a seat reservation by a user.

    Attributes:
        id: Primary key
        seat_id: Foreign key to seats table (unique - one booking per seat)
        user_id: Foreign key to users table
        booked_at: Timestamp when booking was made
    """

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    seat_id = Column(
        Integer,
        ForeignKey("seats.id", ondelete="CASCADE"),
        unique=True,  # Ensures one booking per seat
        nullable=False,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    booked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    seat = relationship("Seat", back_populates="booking")
    user = relationship("User", backref="bookings")

    def __repr__(self) -> str:
        return f"<Booking seat_id={self.seat_id} user_id={self.user_id}>"
