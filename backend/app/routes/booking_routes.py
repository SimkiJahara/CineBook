from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.booking import BookingCreate, BookingRead
from app.controllers.booking_controller import (
    create_booking,
    get_bookings_for_user,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingRead)
def create_booking_route(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
):
    """
    POST /bookings/

    Frontend will call this after payment is confirmed.
    It creates:
    - one row in bookings table
    - many rows in booked_seats table
    """
    return create_booking(db, booking_in)


@router.get("/", response_model=list[BookingRead])
def get_user_bookings_route(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    GET /bookings/?user_id=123

    Returns all bookings for this user.
    Later you can replace user_id with auth token.
    """
    return get_bookings_for_user(db, user_id)
