"""User-related schemas."""

from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .booking import Booking
    from .promocode import Promocode
    from .theater import Theater
    from .screening_draft import Screeningdraft


class UserBase(BaseModel):
    email: str
    name: str
    role: str  # 'TheatreOwner', 'Buyer', 'Superadmin', 'TheaterOwner'


class UserCreate(UserBase):
    passwordhash: str


class User(UserBase):
    id: int
    passwordhash: str

    model_config = ConfigDict(from_attributes=True)


class BuyerBase(BaseModel):
    fullname: str


class BuyerCreate(UserCreate, BuyerBase):
    pass


class Buyer(User, BuyerBase):
    booking: Optional[List["Booking"]] = []

    model_config = ConfigDict(from_attributes=True)


class SuperadminBase(BaseModel):
    pass


class SuperadminCreate(UserCreate, SuperadminBase):
    pass


class Superadmin(User, SuperadminBase):
    promocode: Optional[List["Promocode"]] = []

    model_config = ConfigDict(from_attributes=True)


class TheaterownerBase(BaseModel):
    businessname: str
    ownername: str
    phone: Optional[str] = None
    licensenumber: Optional[str] = None
    bankdetails: Optional[dict] = None
    logourl: Optional[str] = None


class TheaterownerCreate(UserCreate, TheaterownerBase):
    pass


class Theaterowner(User, TheaterownerBase):
    screeningdraft: Optional[List["Screeningdraft"]] = []
    theater: Optional[List["Theater"]] = []

    model_config = ConfigDict(from_attributes=True)