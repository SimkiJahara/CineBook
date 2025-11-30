"""
Controller functions for bookings.

Here we write simple Python functions that:
- talk to the database (via SQLAlchemy session)
- use our Booking and BookedSeat models
"""

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.booking import Booking, BookingSeat
from app.schemas.booking import BookingCreate, BookingRead


def create_booking(db: Session, booking_in: BookingCreate) -> Booking:
    """
    Create a booking in the database.
    If seat_codes is not provided, use the default seats: A1, A2, A3.
    """

    # ✅ 1. Decide which seats to use
    # If frontend sends seat_codes -> use those
    # If not -> use default fake seats
    seat_codes = booking_in.seat_codes or ["A1", "A2", "A3"]

    # ✅ 2. Create the main booking row
    booking = Booking(
        user_id=booking_in.user_id,
        screening_id=booking_in.screening_id,
        total_price=booking_in.total_price,
        payment_method=booking_in.payment_method,
        payment_status=booking_in.payment_status,
        created_at=datetime.utcnow(),
    )

    db.add(booking)
    db.flush()  # so that booking.id is available

    # ✅ 3. Create seat rows (one per seat_code)
    for code in seat_codes:
        # very simple split: first char = row, rest = number (like "A1", "B12")
        row = code[0]
        number_part = code[1:] if len(code) > 1 else "0"

        try:
            number = int(number_part)
        except ValueError:
            number = 0  # fall back if something weird comes

        seat = BookingSeat(
            booking_id=booking.id,
            seat_row=row,
            seat_number=number,
            seat_code=code,
        )
        db.add(seat)

    # ✅ 4. Save to DB
    db.commit()
    db.refresh(booking)

    return booking


def get_bookings_for_user(db: Session, user_id: int) -> list[Booking]:
    """
    Get all bookings for one user.
    Returns a list of Booking objects.
    """

    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return bookings
