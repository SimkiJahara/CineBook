# app/controllers/booking_controller.py

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.booking import Booking, BookedSeat
from app.schemas.booking import BookingCreate, BookingRead


def create_booking(db: Session, booking_in: BookingCreate) -> Booking:
    """
    Create a booking in the database.

    - If booking_in.seats is provided, use those.
    - If not, fall back to default ["A1", "A2", "A3"].
    - total_price = number_of_seats * seat_price
    """

    # 1) Decide which seats to use
    seats_to_use = booking_in.seats or ["A1", "A2", "A3"]

    # 2) Compute total price
    total_price = len(seats_to_use) * booking_in.seat_price

    # 3) Create main booking row
    booking = Booking(
        user_id=booking_in.user_id,
        screening_id=booking_in.screening_id,
        total_price=total_price,
        payment_method=booking_in.payment_method,
        payment_status="PAID",  # fixed for now
        created_at=datetime.utcnow(),
    )

    db.add(booking)
    db.flush()  # to get booking.id

    # 4) Create BookedSeat rows (match your model: seat_label + price)
    for code in seats_to_use:
        seat = BookedSeat(
            booking_id=booking.id,
            seat_label=code,
            price=booking_in.seat_price,
        )
        db.add(seat)

    # 5) Save everything
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
