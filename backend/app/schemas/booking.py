# app/schemas/booking.py

"""
Pydantic schemas for booking API.

BookingCreate:
    Used when a user creates a new booking.
    One booking = one screening + many seats.

BookingRead:
    Used when returning a booking from the API.
    Includes list of booked seats.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class BookedSeatBase(BaseModel):
    """
    Common fields for a booked seat.
    One row = one seat, like 'A1' or 'B5'.
    """

    seat_label: str
    price: float


class BookedSeatRead(BookedSeatBase):
    """
    Seat info returned by the API.
    """

    id: int

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    """
    Common fields for a booking.
    One booking is one user + one screening.
    """

    user_id: int
    screening_id: int
    total_price: float
    payment_method: str
    payment_status: str = "PAID"
    # ✅ seat_codes is now OPTIONAL
    # If frontend does not send this, we will use default ["A1", "A2", "A3"]
    seat_codes: Optional[List[str]] = None


# app/schemas/booking.py

class BookingCreate(BaseModel):
    """
    Schema used when creating a new booking.

    For now, we keep it simple:
    - backend fills user_id from auth if not provided
    - frontend sends screening_id
    - frontend sends list of seat labels
    - frontend sends price per seat
    """

    # 🔑 make this optional so frontend is not forced to send it
    user_id: int | None = None

    screening_id: int

    seats: List[str]
    seat_price: float

    payment_method: str  # "bkash", "nagad", "card"



class BookingRead(BookingBase):
    """
    Schema used when we return a booking from the API.
    Includes:
    - booking id
    - created_at
    - list of booked seats
    """

    id: int
    created_at: datetime
    seats: List[BookedSeatRead]

    class Config:
        from_attributes = True
