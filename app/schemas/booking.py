"""
Pydantic Schemas for Booking and Seat Reservation.

This module defines the data structures used for handling seat reservations, 
booking confirmation requests, API responses, and real-time WebSocket communication 
regarding seat status.
"""

from typing import List, Optional, Literal 
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict 
from app.models.seat import SeatStatus # Adjusted import for app structure

# --- Schemas for Seat Status and Data Transfer ---

class ShowSeatBase(BaseModel):
    """
    Base schema for representing a seat's status within a specific show.
    """
    show_id: int = Field(..., description="The ID of the screening (Show) this seat belongs to.")
    seat_id: int = Field(..., description="The internal ID of the physical seat.")
    status: SeatStatus = Field(..., description="The two-phase commit status: Available, Pending, or Booked.")

class ShowSeatResponse(ShowSeatBase):
    """
    Detailed response schema for a single seat's status, including reservation metadata.

    :ivar id: The primary key ID of the ShowSeat record in the database.
    :vartype id: int
    :ivar reserved_by_user_id: The ID of the user currently holding the seat, if status is PENDING.
    :vartype reserved_by_user_id: Optional[int]
    :ivar hold_expiry_time: The timestamp when the PENDING reservation expires.
    :vartype hold_expiry_time: Optional[datetime]
    :ivar seat_number: The physical number/label of the seat (e.g., '12').
    :vartype seat_number: Optional[str]
    :ivar row_number: The physical row identifier (e.g., 'A').
    :vartype row_number: Optional[str]
    """
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
    """
    Request schema for initiating a seat hold (Phase 1).
    """
    show_id: int = Field(..., description="The ID of the show to hold seats for.")
    seat_ids: List[int] = Field(..., description="A list of physical seat IDs to reserve (e.g., Seat.id).")

class ReserveResponse(BaseModel):
    """
    Response schema after successfully holding seats.
    """
    message: str = Field(..., description="A friendly message confirming the hold.")
    seats: List[ShowSeatResponse] = Field(..., description="The list of ShowSeat records created/updated with PENDING status.")
    hold_duration_seconds: int = Field(..., description="The total duration (in seconds) the seats are held for.")

class ConfirmRequest(BaseModel):
    """
    Request schema for confirming a held reservation and processing payment (Phase 2).
    """
    show_id: int = Field(..., description="The ID of the show to confirm the booking for.")
    seat_ids: List[int] = Field(..., description="The list of physical seat IDs to confirm.")
    payment_token: str = Field(..., description="The token received from the payment gateway.")
    total_price: int = Field(..., description="The total price of the booking.")

class BookingResponse(BaseModel):
    """
    Response schema detailing the final confirmed booking record.

    :ivar id: The unique ID of the final Booking transaction.
    :vartype id: int
    :ivar user_id: The ID of the user (Buyer) who made the booking.
    :vartype user_id: int
    :ivar show_id: The ID of the screening booked.
    :vartype show_id: int
    :ivar total_price: The final price paid.
    :vartype total_price: int
    :ivar booking_time: The time the booking was confirmed.
    :vartype booking_time: datetime
    :ivar status: The final booking status (e.g., 'CONFIRMED').
    :vartype status: str
    :ivar booked_seats: List of ShowSeat IDs that were successfully transitioned to BOOKED status.
    :vartype booked_seats: List[int]
    """
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
    """
    Schema for broadcasting real-time seat status updates to WebSocket clients.
    """
    event: Literal["seat_update"] = Field("seat_update", description="The type of event being broadcasted.")
    show_id: int = Field(..., description="The show ID to which this update applies.")
    seats: List[ShowSeatResponse] = Field(..., description="A list of seats and their updated statuses.")