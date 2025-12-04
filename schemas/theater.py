"""Theater and Hall schemas."""

from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .user import Theaterowner
    from .screening import Screening
    from .booking import Booking


class TheaterBase(BaseModel):
    companyid: str
    branchid: str
    name: str
    address: str
    ownerid: int
    contact: Optional[str] = None
    logourl: Optional[str] = None
    isverified: Optional[bool] = False


class TheaterCreate(TheaterBase):
    pass


class Theater(TheaterBase):
    theaterowner: Optional["Theaterowner"] = None
    hall: Optional[List["Hall"]] = []

    model_config = ConfigDict(from_attributes=True)


class HallBase(BaseModel):
    hallid: str
    companyid: str
    branchid: str
    capacity: int


class HallCreate(HallBase):
    pass


class Hall(HallBase):
    theater: Optional[Theater] = None
    screening: Optional[List["Screening"]] = []

    model_config = ConfigDict(from_attributes=True)


class SeatlayoutBase(BaseModel):
    layouthallid: str
    layoutcompanyid: str
    layoutbranchid: str
    # Inherited from Hall
    capacity: int


class SeatlayoutCreate(SeatlayoutBase):
    pass


class Seatlayout(SeatlayoutBase):
    # Hall fields (since Seatlayout inherits from Hall in ORM)
    hallid: str
    companyid: str
    branchid: str
    seat: Optional[List["Seat"]] = []

    model_config = ConfigDict(from_attributes=True)


class SeatBase(BaseModel):
    seatid: str
    layouthallid: str
    layoutcompanyid: str
    layoutbranchid: str
    rownumber: str
    number: int
    type: Optional[str] = None
    status: Optional[str] = "AVAILABLE"


class SeatCreate(SeatBase):
    pass


class Seat(SeatBase):
    booking: Optional[List["Booking"]] = []
    seatlayout: Optional[Seatlayout] = None

    model_config = ConfigDict(from_attributes=True)