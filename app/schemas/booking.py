"""
Booking Schemas
===============

This module defines the Pydantic data models used for the theater booking system.
These schemas are crucial for validating incoming API requests and structuring
outgoing responses related to seats, bookings, and theater layouts.

Key Models:
- **SeatBase**: The fundamental properties of a seat.
- **SeatResponse**: Extends SeatBase with operational data like ID and booking status.
- **BookingCreate**: Minimal model for creating a new booking (requires only a seat ID).
- **BookingResponse**: Comprehensive response model for a successful booking.
- **TheaterResponse**: Used to represent the full state of the theater, including all seats and summary statistics.
- **BookingStatusResponse**: Used for general booking operation feedback (success/failure messages).
"""
# =============================================================================
# Booking Schemas - Pydantic Models for Request/Response Validation
# =============================================================================
# Pydantic V2 schemas for the booking system endpoints.
# =============================================================================

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SeatBase(BaseModel):
    """Base schema for seat data."""

    row: str
    number: int
    seat_type: str
    price: float


class SeatResponse(SeatBase):
    """
    Response schema for a seat with booking status.

    Attributes:
        id: Seat ID
        row: Row identifier (A, B, C, etc.)
        number: Seat number
        seat_type: 'standard' or 'vip'
        price: Price in Taka
        is_booked: Whether the seat is already booked
        booked_by_current_user: Whether current user booked this seat
    """

    id: int
    is_booked: bool = False
    booked_by_current_user: bool = False

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    """Schema for creating a booking - just needs seat_id."""

    seat_id: int


class BookingResponse(BaseModel):
    """
    Response schema for a booking.

    Attributes:
        id: Booking ID
        seat_id: ID of the booked seat
        user_id: ID of the user who made the booking
        booked_at: Timestamp of booking
        seat: Seat details
    """

    id: int
    seat_id: int
    user_id: int
    booked_at: datetime
    seat: SeatBase

    model_config = ConfigDict(from_attributes=True)


class TheaterResponse(BaseModel):
    """
    Response schema for the entire theater layout.

    Attributes:
        seats: List of all seats with their booking status
        total_seats: Total number of seats
        available_seats: Number of available seats
        booked_seats: Number of booked seats
    """

    seats: List[SeatResponse]
    total_seats: int
    available_seats: int
    booked_seats: int


class BookingStatusResponse(BaseModel):
    """Response for booking operation status."""

    success: bool
    message: str
    booking: Optional[BookingResponse] = None