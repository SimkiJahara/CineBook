"""
This module manages all location related entities:
- Addresses
- Cities
- Halls
- Screenings
- Theaters

It provides helper functions and  route definitions for:
- Creating new records
- Fetching lists of existing records
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Address, City, Hall, Screening, Theater
from app.schemas.location import (
    AddressCreate, AddressRead,
    CityCreate, CityRead,
    HallCreate, HallRead,
    ScreeningCreate, ScreeningRead,
    TheaterCreate, TheaterRead,
)

router = APIRouter()

# Adress related Function and Routers

def create_address(db, address_in):
    """Create a new address"""
    address = Address(
        street=address_in.street,
        area=address_in.area,
        postal_code=address_in.postal_code,
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def get_all_addresses(db):
    """return all addresses"""
    return db.query(Address).all()


@router.post("/addresses/", response_model=AddressRead, tags=["Addresses"])
def create_address_route(address: AddressCreate, db=Depends(get_db)):
    return create_address(db, address)


@router.get("/addresses/", response_model=list[AddressRead], tags=["Addresses"])
def get_addresses_route(db=Depends(get_db)):
    return get_all_addresses(db)


# City related Function and Router

def create_city(db, city_data):
    """Create a new city"""
    city = City(name=city_data.name)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


def get_all_cities(db):
    """return all cities"""
    return db.query(City).all()


@router.post("/cities/", response_model=CityRead, tags=["Cities"])
def create_city_route(city: CityCreate, db=Depends(get_db)):
    return create_city(db, city)


@router.get("/cities/", response_model=list[CityRead], tags=["Cities"])
def get_cities_route(db=Depends(get_db)):
    return get_all_cities(db)


# Hall Related Function and Routers
def create_hall(db, hall_data):
    """Create a new hall"""
    hall = Hall(
        name=hall_data.name,
        total_seats=hall_data.total_seats,
        theater_id=hall_data.theater_id,
    )
    db.add(hall)
    db.commit()
    db.refresh(hall)
    return hall


def get_all_halls(db):
    """Return all halls"""
    return db.query(Hall).all()


@router.post("/halls/", response_model=HallRead, tags=["Halls"])
def create_hall_route(hall: HallCreate, db=Depends(get_db)):
    return create_hall(db, hall)


@router.get("/halls/", response_model=list[HallRead], tags=["Halls"])
def get_halls_route(db=Depends(get_db)):
    return get_all_halls(db)


# Screening related Function and Routers

def create_screening(db, screening_data):
    """creates a new screening"""
    
    screening = Screening(
        movie_id=screening_data.movie_id,
        hall_id=screening_data.hall_id,
        show_date=screening_data.show_date,
        start_time=screening_data.start_time,
        end_time=screening_data.end_time,
        base_price=screening_data.base_price,
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)
    return screening


def get_all_screenings(db):
    """it returns all screenings"""
    return db.query(Screening).all()


@router.post("/screenings/", response_model=ScreeningRead, tags=["Screenings"])
def create_screening_route(screening: ScreeningCreate, db=Depends(get_db)):
    return create_screening(db, screening)


@router.get("/screenings/", response_model=list[ScreeningRead], tags=["Screenings"])
def get_screenings_route(db=Depends(get_db)):
    return get_all_screenings(db)


# Theater related function and routers

def create_theater(db, theater_data):
    """Create a new theater"""
    theater = Theater(
        name=theater_data.name,
        description=theater_data.description,
        contact_email=theater_data.contact_email,
        contact_phone=theater_data.contact_phone,
        city_id=theater_data.city_id,
        address_id=theater_data.address_id,
    )
    db.add(theater)
    db.commit()
    db.refresh(theater)
    return theater


def get_all_theaters(db):
    """it returns all theaters"""
    return db.query(Theater).all()


@router.post("/theaters/", response_model=TheaterRead, tags=["Theaters"])
def create_theater_route(theater: TheaterCreate, db=Depends(get_db)):
    return create_theater(db, theater)


@router.get("/theaters/", response_model=list[TheaterRead], tags=["Theaters"])
def get_theaters_route(db=Depends(get_db)):
    return get_all_theaters(db)
