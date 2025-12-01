# app/schemas/location.py

from datetime import date, time, datetime
from pydantic import BaseModel


# City
class CityCreate(BaseModel):
    name: str


class CityRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# Address
class AddressCreate(BaseModel):
    street: str
    area: str
    postal_code: str


class AddressRead(BaseModel):
    id: int
    street: str
    area: str
    postal_code: str

    class Config:
        from_attributes = True


# Theater
class TheaterCreate(BaseModel):
    name: str
    description: str | None = None
    contact_email: str
    contact_phone: str
    city_id: int
    address_id: int


class TheaterRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    contact_email: str
    contact_phone: str
    city_id: int
    address_id: int

    class Config:
        from_attributes = True


# Hall
class HallCreate(BaseModel):
    name: str
    total_seats: int
    theater_id: int


class HallRead(BaseModel):
    id: int
    name: str
    total_seats: int
    theater_id: int

    class Config:
        from_attributes = True


# Screening
class ScreeningCreate(BaseModel):
    movie_id: int
    hall_id: int
    show_date: date
    start_time: time
    end_time: time | None = None
    base_price: float


class ScreeningRead(BaseModel):
    id: int
    movie_id: int
    hall_id: int
    show_date: date
    start_time: time
    end_time: time | None = None
    base_price: float
    created_at: datetime

    class Config:
        from_attributes = True
