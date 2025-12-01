# app/controllers/booking_controller.py

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookedSeat
from app.schemas.booking import BookingCreate, BookingRead
from app.utils.auth import get_current_user, MockUser

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def create_booking(db, booking_in):
    """
    Create a booking record.
    Seats use a small default list if none is given.
    """
    seats = booking_in.seats or ["A1", "A2", "A3"]
    total_price = len(seats) * booking_in.seat_price

    booking = Booking(
        user_id=booking_in.user_id,
        screening_id=booking_in.screening_id,
        total_price=total_price,
        payment_method=booking_in.payment_method,
        payment_status="PAID",
        created_at=datetime.utcnow(),
    )

    db.add(booking)
    db.flush()

    for seat in seats:
        seat_row = BookedSeat(
            booking_id=booking.id,
            seat_label=seat,
            price=booking_in.seat_price,
        )
        db.add(seat_row)

    db.commit()
    db.refresh(booking)
    return booking


def get_bookings_for_user(db, user_id):
    """
    Return bookings for one user.
    """
    return (
        db.query(Booking)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.post("/", response_model=BookingRead)
def create_booking_route(
    booking_in: BookingCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a booking for the current user.
    """
    if booking_in.user_id is None:
        booking_in.user_id = current_user.id
    return create_booking(db, booking_in)


@router.get("/", response_model=list[BookingRead])
def list_bookings_route(
    user_id: int,
    db=Depends(get_db),
):
    """
    Basic route to return bookings by user_id.
    """
    return get_bookings_for_user(db, user_id)


@router.get("/me", response_model=list[BookingRead])
def list_my_bookings_route(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return bookings for the logged-in user.
    """
    return get_bookings_for_user(db, current_user.id)
