# app/routes/booking_routes.py

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.booking import BookingCreate, BookingRead
from app.controllers.booking_controller import create_booking, get_bookings_for_user

# 👇 import the fake auth like your movie module does
from app.utils.auth import get_current_user, MockUser

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingRead)
def create_booking_route(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_current_user),
):
    """
    Create a booking for the *current* user.

    - If booking_in.user_id is missing or None -> fill it from current_user.id
    - Seat selection is still fake (A1,A2,A3) inside the controller if not provided.
    """

    # 🔑 If user_id not provided in body, fill from fake auth
    if booking_in.user_id is None:
        booking_in.user_id = current_user.id

    return create_booking(db, booking_in)


@router.get("/", response_model=List[BookingRead])
def list_bookings_route(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Old style: /bookings/?user_id=1

    Kept for testing / Swagger manually.
    """
    return get_bookings_for_user(db, user_id)


@router.get("/me", response_model=List[BookingRead])
def list_my_bookings_route(
    db: Session = Depends(get_db),
    current_user: MockUser = Depends(get_current_user),
):
    """
    New style: /bookings/me

    Uses fake auth user (MockUser) instead of passing user_id query param.
    """
    return get_bookings_for_user(db, current_user.id)
