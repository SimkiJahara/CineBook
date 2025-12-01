# /api/v1/endpoints/bookings.py

"""
API Endpoints for Managing Bookings and Seat Reservations.

This module provides the necessary routes for users to reserve and confirm seats
for a specific show. It integrates with the database and authentication services.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db # Assuming get_db is defined in core.db
from app.core.security import get_current_user # Assuming a function to get current user
from app.services import booking_service
from app.schemas.booking import ReserveRequest, ReserveResponse, ConfirmRequest, BookingResponse
# from models.user import User # Import User model for dependency injection type hint

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)

@router.post("/reserve", response_model=ReserveResponse, status_code=status.HTTP_200_OK)
async def reserve_seats(
    request: ReserveRequest,
    db: Session = Depends(get_db),
    # Assuming get_current_user returns a user object with an 'id' attribute
    current_user: dict = Depends(get_current_user) 
):
    """
    API Endpoint for holding seats (Phase 1: Hold/Pending).

    This endpoint temporarily holds the specified seats for a user, initiating the
    reservation process. The held seats are released if payment is not completed
    within the hold duration.

    :param request: The request body containing the show ID and list of seat IDs to hold.
    :type request: app.schemas.booking.ReserveRequest
    :param db: The database session dependency.
    :type db: sqlalchemy.orm.Session
    :param current_user: The authenticated user object (must have an 'id' attribute).
    :type current_user: dict
    :return: A response detailing the successfully held seats and the hold duration.
    :rtype: app.schemas.booking.ReserveResponse
    """
    
    reserved_seats, hold_duration = await booking_service.reserve_seats(
        db=db,
        show_id=request.show_id,
        user_id=current_user.id, # Use the user ID from the authenticated user
        seat_ids=request.seat_ids
    )

    return ReserveResponse(
        message="Seats successfully held. Please complete payment within the expiry time.",
        seats=reserved_seats,
        hold_duration_seconds=hold_duration
    )

@router.post("/confirm", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def confirm_booking(
    request: ConfirmRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    API Endpoint for confirming a held reservation (Phase 2: Confirmation/Payment).

    This endpoint finalizes a reservation by processing the payment token for seats
    that were previously held. If successful, a permanent booking record is created.

    :param request: The request body containing the show ID, seat IDs, payment token, and total price.
    :type request: app.schemas.booking.ConfirmRequest
    :param db: The database session dependency.
    :type db: sqlalchemy.orm.Session
    :param current_user: The authenticated user object (must have an 'id' attribute).
    :type current_user: dict
    :raises: HTTPException 400 (Bad Request) if the reservation is expired or seats are unavailable.
    :return: The newly created booking record details.
    :rtype: app.schemas.booking.BookingResponse
    """
    
    booking_record = await booking_service.confirm_booking(
        db=db,
        user_id=current_user.id, # Use the user ID from the authenticated user
        show_id=request.show_id,
        seat_ids=request.seat_ids,
        payment_token=request.payment_token,
        total_price=request.total_price
    )
    
    return booking_record