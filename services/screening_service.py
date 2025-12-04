from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, date, time
from typing import Optional, Dict, List
from decimal import Decimal

# Import ORM models
from models import (
    Screening, Movie, Hall, Theater, Theaterowner, 
    Booking, Seat, User
)

# Import Pydantic schemas
from schemas import (
    ScreeningCreate, ScreeningBase, Screening as ScreeningSchema
)

# Database session dependency
from database import get_db

# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------

def get_owner_theaters_and_halls(db: Session, owner_id: int):
    """Retrieve all theaters and their associated halls for a theater owner.

    This function first validates that the theater owner exists. If the owner
    is found, it retrieves all theaters associated with that owner and then
    collects all halls belonging to each of those theaters.

    Args:
        db (Session): SQLAlchemy database session.
        owner_id (int): ID of the theater owner.

    Returns:
        tuple:
            A tuple `(theaters, halls)` where:
            
            - theaters (list[Theater]): All theaters owned by the specified owner.
            - halls (list[Hall]): All halls corresponding to those theaters.

    Raises:
        HTTPException: If no owner exists with the given ID (404).
    """
    
    owner = db.query(Theaterowner).filter(Theaterowner.id == owner_id).first()
    
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    # Get all theaters owned by this owner
    theaters = db.query(Theater).filter(Theater.ownerid == owner_id).all()
    
    # Get all halls for these theaters
    halls = []
    for theater in theaters:
        theater_halls = db.query(Hall).filter(
            Hall.companyid == theater.companyid,
            Hall.branchid == theater.branchid
        ).all()
        halls.extend(theater_halls)
    
    return theaters, halls


def get_active_movies(db: Session):
    """Retrieve all currently active movies.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        list[Movie]: A list of active movie records.
    """
    return db.query(Movie).filter(Movie.is_active == 1).all()


def get_screenings_for_hall_and_date(
    db: Session, 
    hallid: str, 
    companyid: str, 
    branchid: str, 
    screening_date: date
):
    """Retrieve all screenings for a hall on a specified date.

    Args:
        db (Session): SQLAlchemy database session.
        hallid (str): Hall ID.
        companyid (str): Company ID of the hall.
        branchid (str): Branch ID of the hall.
        screening_date (date): Date for which screenings should be retrieved.

    Returns:
        list[Screening]: A list of screening records ordered by start time.

    Raises:
        None
    """
    return db.query(Screening).filter(
        Screening.hallid == hallid,
        Screening.hallcompanyid == companyid,
        Screening.hallbranchid == branchid,
        Screening.date == screening_date
    ).order_by(Screening.starttime).all()


def calculate_revenue_for_screening(db: Session, screening_id: int):
    """Calculate the total confirmed revenue for a screening.

    This function sums the `totalamount` of all bookings with
    status `"CONFIRMED"`.

    Args:
        db (Session): SQLAlchemy database session.
        screening_id (int): The ID of the screening.

    Returns:
        Decimal: Total confirmed revenue for the screening. Returns
        `Decimal('0.00')` if no revenue exists.

    Raises:
        None
    """
    total = db.query(func.sum(Booking.totalamount)).filter(
        Booking.screeningid == screening_id,
        Booking.status == 'CONFIRMED'  # Only count confirmed bookings
    ).scalar()
    
    return total or Decimal('0.00')
