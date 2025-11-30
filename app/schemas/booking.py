# /app/schemas/booking.py

from typing import List, Optional, Literal # <-- NOTE: Added 'Literal' for Pydantic v2 compatibility
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict # NOTE: ConfigDict is used for Pydantic v2 models
from app.models.seat import SeatStatus # Adjusted import for app structure

# --- Schemas for Seat Status and Data Transfer ---

class ShowSeatBase(BaseModel):
    show_id: int
    seat_id: int
    status: SeatStatus = Field(..., description="The two-phase commit status: Available, Pending, or Booked.")

class ShowSeatResponse(ShowSeatBase):
    id: int
    reserved_by_user_id: Optional[int] = None
    hold_expiry_time: Optional[datetime] = None
    seat_number: Optional[str] = None
    row_number: Optional[str] = None

    # Pydantic V2 Config
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )

# --- Schemas for API Requests ---

class ReserveRequest(BaseModel):
    show_id: int = Field(..., description="The ID of the show to hold seats for.")
    seat_ids: List[int] = Field(..., description="A list of physical seat IDs to reserve (e.g., Seat.id).")

class ReserveResponse(BaseModel):
    message: str
    seats: List[ShowSeatResponse]
    hold_duration_seconds: int

class ConfirmRequest(BaseModel):
    show_id: int = Field(..., description="The ID of the show to confirm the booking for.")
    seat_ids: List[int] = Field(..., description="The list of physical seat IDs to confirm.")
    payment_token: str = Field(..., description="The token received from the payment gateway.")
    total_price: int = Field(..., description="The total price of the booking.")

class BookingResponse(BaseModel):
    id: int
    user_id: int
    show_id: int
    total_price: int
    booking_time: datetime
    status: str
    booked_seats: List[int] # List of ShowSeat IDs confirmed

    # Pydantic V2 Config
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )
        
# --- Schema for WebSocket Broadcasts (The Fix) ---

class WebSocketSeatUpdate(BaseModel):
    # FIX: Replaced Field(..., const=True) with Literal
    event: Literal["seat_update"] = "seat_update" 
    show_id: int
    seats: List[ShowSeatResponse]