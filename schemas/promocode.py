"""Booking schema."""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .user import Buyer
    from .promocode import Promocode
    from .screening import Screening
    from .theater import Seat


class BookingBase(BaseModel):
    totalamount: Decimal
    paymentmethod: str
    status: str = "PENDING"
    buyerid: int
    screeningid: int
    qrcodeurl: Optional[str] = None
    promocode: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    bookingid: int
    bookedat: Optional[datetime] = None
    buyer: Optional["Buyer"] = None
    promocode_: Optional["Promocode"] = None
    screening: Optional["Screening"] = None
    seat: Optional[List["Seat"]] = []

    model_config = ConfigDict(from_attributes=True)