"""This Module database schemas for Booking and BookedSeat models"""

from datetime import datetime
from pydantic import BaseModel


class BookedSeatRead(BaseModel):
    """it returns seat info"""
    id: int
    seat_label: str
    price: float

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """Data needed to make a new booking"""
    user_id: int | None = None
    screening_id: int
    seats: list[str]
    seat_price: float
    payment_method: str


class BookingRead(BaseModel):
    """it returns booking info"""
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
