# app/schemas/booking.py

from datetime import datetime
from pydantic import BaseModel


class BookedSeatRead(BaseModel):
    """Seat info returned from the API."""
    id: int
    seat_label: str
    price: float

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """Data needed to make a new booking."""
    user_id: int | None = None
    screening_id: int
    seats: list[str]
    seat_price: float
    payment_method: str


class BookingRead(BaseModel):
    """Booking info returned from the API."""
    id: int
    user_id: int
    screening_id: int
    total_price: float
    payment_method: str
    payment_status: str
    created_at: datetime
    seats: list[BookedSeatRead]

    class Config:
        from_attributes = True
