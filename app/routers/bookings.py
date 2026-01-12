# =============================================================================
# Bookings Router - API Endpoints for Seat Booking


from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.booking import (
    SeatResponse,
    BookingResponse,
    TheaterResponse,
    BookingStatusResponse,
)
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/seats", response_model=TheaterResponse)
async def get_theater_seats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
) -> TheaterResponse:
    """
    Get all seats with their booking status.

    Public endpoint - shows theater layout to everyone.
    If authenticated, also shows which seats the current user has booked.

    Returns:
        TheaterResponse with all seats and statistics
    """
    user_id = current_user.id if current_user else None
    return booking_service.get_theater_layout(db, user_id)


@router.post("/book/{seat_id}", response_model=BookingStatusResponse)
async def book_seat(
    seat_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BookingStatusResponse:
    """
    Book a seat for the current authenticated user.

    Uses PostgreSQL transaction locking to prevent double-booking.

    Args:
        seat_id: ID of the seat to book

    Returns:
        BookingStatusResponse with success status and booking details

    Raises:
        HTTPException 400: If seat is already booked or not found
        HTTPException 401: If user is not authenticated
    """
    success, message, booking = booking_service.book_seat(db, seat_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    booking_response = None
    if booking:
        booking_response = BookingResponse(
            id=booking.id,
            seat_id=booking.seat_id,
            user_id=booking.user_id,
            booked_at=booking.booked_at,
            seat={
                "row": booking.seat.row,
                "number": booking.seat.number,
                "seat_type": booking.seat.seat_type,
                "price": booking.seat.price,
            },
        )

    return BookingStatusResponse(
        success=True,
        message=message,
        booking=booking_response,
    )


@router.delete("/cancel/{booking_id}", response_model=BookingStatusResponse)
async def cancel_booking(
    booking_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BookingStatusResponse:
    """
    Cancel a booking (only the user who made it can cancel).

    Args:
        booking_id: ID of the booking to cancel

    Returns:
        BookingStatusResponse with success status

    Raises:
        HTTPException 400: If booking not found or belongs to another user
        HTTPException 401: If user is not authenticated
    """
    success, message = booking_service.cancel_booking(db, booking_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return BookingStatusResponse(
        success=True,
        message=message,
    )


@router.get("/my-bookings", response_model=List[BookingResponse])
async def get_my_bookings(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[BookingResponse]:
    """
    Get all bookings for the current authenticated user.

    Returns:
        List of BookingResponse objects

    Raises:
        HTTPException 401: If user is not authenticated
    """
    bookings = booking_service.get_user_bookings(db, current_user.id)

    return [
        BookingResponse(
            id=booking.id,
            seat_id=booking.seat_id,
            user_id=booking.user_id,
            booked_at=booking.booked_at,
            seat={
                "row": booking.seat.row,
                "number": booking.seat.number,
                "seat_type": booking.seat.seat_type,
                "price": booking.seat.price,
            },
        )
        for booking in bookings
    ]
