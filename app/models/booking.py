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
    """
    Seat type enumeration for pricing tiers.

    Used to categorize seats within the database and link to pricing information.

    :ivar STANDARD: Standard seating area.
    :vartype STANDARD: str
    :ivar VIP: Premium or VIP seating area.
    :vartype VIP: str
    """

    STANDARD = "standard"
    VIP = "vip"


class Seat(Base):
    """
    Seat model representing a single seat in the theater.

    This model stores the physical characteristics and base price of a seat.

    :ivar id: Primary key of the seat.
    :vartype id: int
    :ivar row: Row identifier (e.g., 'A', 'B', 'C').
    :vartype row: str
    :ivar number: Seat number within the row (1, 2, 3...).
    :vartype number: int
    :ivar seat_type: Type of seat (standard/vip) for pricing. Defaults to 'standard'.
    :vartype seat_type: str
    :ivar price: Base price of the seat in Taka.
    :vartype price: float
    :ivar booking: Relationship to the :class:`Booking` model.
    :vartype booking: :class:`Booking`
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

    This model enforces a one-to-one relationship between a booking and a seat
    via the ``seat_id`` unique constraint.

    :ivar id: Primary key of the booking.
    :vartype id: int
    :ivar seat_id: Foreign key to the :class:`Seat` table. Unique constraint ensures one booking per seat.
    :vartype seat_id: int
    :ivar user_id: Foreign key to the :class:`User` table.
    :vartype user_id: int
    :ivar booked_at: Timestamp when the booking was made. Defaults to the current time.
    :vartype booked_at: :class:`datetime.datetime`
    :ivar seat: Relationship to the :class:`Seat` model.
    :vartype seat: :class:`Seat`
    :ivar user: Relationship to the :class:`User` model.
    :vartype user: :class:`User`
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