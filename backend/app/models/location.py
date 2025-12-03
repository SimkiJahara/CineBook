"""
This module contains Location models:
- City: Represents a city where theaters are located.
- Address: Represents physical addresses.
- Theater: Represents a movie theater belongs to a city and address.
- Hall: Represents a hall inside a theater.
- Screening: Represents a scheduled movie screening inside a hall.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
)

from app.database import Base


class City(Base):
    """for city table in database"""

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)


class Address(Base):
    """for address table in database"""

    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)


class Theater(Base):
    """for theater table in database"""

    __tablename__ = "theaters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(300), nullable=True)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)


class Hall(Base):
    """for hall table in database"""

    __tablename__ = "halls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    total_seats = Column(Integer, nullable=False)
    theater_id = Column(Integer, ForeignKey("theaters.id"), nullable=False)


class Screening(Base):
    """for Screening table in database"""

    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)
    show_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
