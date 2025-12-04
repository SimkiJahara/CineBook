"""Screening schema."""

from typing import Optional, List, TYPE_CHECKING
from datetime import date, time
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .theater import Hall
    from .movie import Movie
    from .booking import Booking


class ScreeningBase(BaseModel):
    date: date
    starttime: time
    status: str = "SCHEDULED"
    movieeidr: str
    hallid: str
    hallcompanyid: str
    hallbranchid: str


class ScreeningCreate(ScreeningBase):
    pass


class Screening(ScreeningBase):
    id: int
    hall: Optional["Hall"] = None
    movie: Optional["Movie"] = None
    booking: Optional[List["Booking"]] = []

    model_config = ConfigDict(from_attributes=True)