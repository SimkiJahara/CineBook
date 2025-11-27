from pydantic import BaseModel
from datetime import date, time, datetime
from pydantic import BaseModel



class CityBase(BaseModel):
    """
    Common fields for City.
    Used as a base for other City schemas.
    """

    name: str


class CityCreate(CityBase):
    """
    Schema used when creating a new city.
    (For example, in POST /cities)
    """
    pass


class CityRead(CityBase):
    """
    Schema used when returning a city in API responses.
    Includes the city ID.
    """

    id: int

    class Config:
        # This tells Pydantic that we will pass ORM objects
        # (like SQLAlchemy City instances) and it should
        # read attributes from them.
        from_attributes = True


class AddressBase(BaseModel):
    """
    Common fields for Address.
    """
    street: str
    area: str
    postal_code: str


class AddressCreate(AddressBase):
    """
    Schema used when creating a new address.
    (POST /addresses)
    """
    pass


class AddressRead(AddressBase):
    """
    Schema used when returning an address in API responses.
    """
    id: int

    class Config:
        from_attributes = True


class TheaterBase(BaseModel):
    """
    Common fields for Theater.
    """

    name: str
    description: str | None = None
    contact_email: str
    contact_phone: str
    city_id: int
    address_id: int


class TheaterCreate(TheaterBase):
    """
    Schema used when creating a new theater.
    (POST /theaters)
    """
    pass


class TheaterRead(TheaterBase):
    """
    Schema used when returning a theater in API responses.
    Includes the theater ID.
    """

    id: int

    class Config:
        from_attributes = True


class HallBase(BaseModel):
    """
    Common fields for Hall.
    """

    name: str
    total_seats: int
    theater_id: int


class HallCreate(HallBase):
    """
    Schema used when creating a new hall.
    (POST /halls)
    """
    pass


class HallRead(HallBase):
    """
    Schema used when returning a hall in API responses.
    """

    id: int

    class Config:
        from_attributes = True


class ScreeningBase(BaseModel):
    """
    Common fields for a Screening.
    One movie in one hall at a specific date and time.
    """

    movie_id: int
    hall_id: int

    show_date: date
    start_time: time
    end_time: time | None = None

    base_price: float


class ScreeningCreate(ScreeningBase):
    """
    Schema used when creating a new screening.
    (POST /screenings)
    """
    pass


class ScreeningRead(ScreeningBase):
    """
    Schema used when returning a screening in API responses.
    Includes id and created_at.
    """

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


