"""
Booking Service
===============

This module contains the business logic for managing theater seats and handling
the booking process. It ensures data integrity, particularly concerning
race conditions, by utilizing PostgreSQL's transaction-based row-level locking
(SELECT ... FOR UPDATE) to prevent double-booking.

Key Functions:
- ``get_all_seats`` and ``get_seat_by_id``: Retrieval of individual seat data.
- ``get_theater_layout``: Provides the full theater view, including real-time booking status.
- ``book_seat``: The core transaction logic, employing row locking for concurrency safety.
- ``cancel_booking``: Allows users to cancel their own reservations.
- ``get_user_bookings``: Retrieves a history of bookings for a specific user.
- ``create_seat`` and ``get_seat_count``: Utility functions for initializing and querying seat data.
"""
# =============================================================================
# Booking Service - Business Logic for Seat Booking
# =============================================================================
# Handles all booking-related operations with PostgreSQL transaction-based
# locking to prevent double-booking. No Redis required.
# =============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.models.booking import Seat, Booking, SeatType
from app.schemas.booking import SeatResponse, BookingResponse, TheaterResponse


def get_all_seats(db: Session) -> List[Seat]:
    """
    Retrieve all seats from the database.

    Args:
        db: Database session

    Returns:
        List of all Seat objects
    """
    return db.query(Seat).order_by(Seat.row, Seat.number).all()


def get_seat_by_id(db: Session, seat_id: int) -> Optional[Seat]:
    """
    Retrieve a specific seat by ID.

    Args:
        db: Database session
        seat_id: ID of the seat to retrieve

    Returns:
        Seat object if found, None otherwise
    """
    return db.query(Seat).filter(Seat.id == seat_id).first()


def get_theater_layout(
    db: Session, current_user_id: Optional[int] = None
) -> TheaterResponse:
    """
    Get the complete theater layout with booking status for each seat.

    Args:
        db: Database session
        current_user_id: ID of the current user (to mark their bookings)

    Returns:
        TheaterResponse with all seats and statistics
    """
    seats = get_all_seats(db)

    seat_responses = []
    booked_count = 0

    for seat in seats:
        is_booked = seat.booking is not None
        booked_by_current_user = False

        if is_booked:
            booked_count += 1
            if current_user_id and seat.booking.user_id == current_user_id:
                booked_by_current_user = True

        seat_responses.append(
            SeatResponse(
                id=seat.id,
                row=seat.row,
                number=seat.number,
                seat_type=seat.seat_type,
                price=seat.price,
                is_booked=is_booked,
                booked_by_current_user=booked_by_current_user,
            )
        )

    return TheaterResponse(
        seats=seat_responses,
        total_seats=len(seats),
        available_seats=len(seats) - booked_count,
        booked_seats=booked_count,
    )


def book_seat(
    db: Session, seat_id: int, user_id: int
) -> tuple[bool, str, Optional[Booking]]:
    """
    Book a seat for a user with PostgreSQL transaction-based locking.

    Uses SELECT ... FOR UPDATE to acquire a row-level lock on the seat,
    preventing double-booking without requiring Redis or in-memory locking.
    

    Args:
        db: Database session
        seat_id: ID of the seat to book
        user_id: ID of the user making the booking

    Returns:
        Tuple of (success: bool, message: str, booking: Optional[Booking])
    """
    try:
        # Use FOR UPDATE to lock the seat row during this transaction
        # This prevents race conditions where two users try to book the same seat
        seat = db.execute(
            select(Seat).where(Seat.id == seat_id).with_for_update()
        ).scalar_one_or_none()

        if not seat:
            return False, "Seat not found", None

        # Check if seat is already booked (within the same locked transaction)
        existing_booking = db.query(Booking).filter(Booking.seat_id == seat_id).first()

        if existing_booking:
            if existing_booking.user_id == user_id:
                return False, "You have already booked this seat", None
            return False, "This seat is already booked by another user", None

        # Create the booking
        booking = Booking(
            seat_id=seat_id,
            user_id=user_id,
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return True, f"Successfully booked seat {seat.row}{seat.number}", booking

    except IntegrityError:
        # Handle race condition where unique constraint is violated
        db.rollback()
        return (
            False,
            "This seat was just booked by someone else. Please try another seat.",
            None,
        )
    except Exception as e:
        db.rollback()
        return False, f"An error occurred: {str(e)}", None


def cancel_booking(db: Session, booking_id: int, user_id: int) -> tuple[bool, str]:
    """
    Cancel a booking (only by the user who made it).

    Args:
        db: Database session
        booking_id: ID of the booking to cancel
        user_id: ID of the user requesting cancellation

    Returns:
        Tuple of (success: bool, message: str)
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        return False, "Booking not found"

    if booking.user_id != user_id:
        return False, "You can only cancel your own bookings"

    seat_info = f"{booking.seat.row}{booking.seat.number}"
    db.delete(booking)
    db.commit()

    return True, f"Successfully cancelled booking for seat {seat_info}"


def get_user_bookings(db: Session, user_id: int) -> List[Booking]:
    """
    Get all bookings for a specific user.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        List of Booking objects for the user
    """
    return db.query(Booking).filter(Booking.user_id == user_id).all()


def create_seat(
    db: Session,
    row: str,
    number: int,
    seat_type: str = SeatType.STANDARD.value,
    price: float = 10.0,
) -> Seat:
    """
    Create a new seat in the database.

    Args:
        db: Database session
        row: Row identifier (e.g., 'A', 'B')
        number: Seat number within the row
        seat_type: 'standard' or 'vip'
        price: Price in Taka

    Returns:
        Created Seat object
    """
    seat = Seat(
        row=row,
        number=number,
        seat_type=seat_type,
        price=price,
    )
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


def get_seat_count(db: Session) -> int:
    """Get the total number of seats in the database."""
    return db.query(Seat).count()