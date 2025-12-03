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
    """Get all theaters and halls belonging to a theater owner"""
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
    """Get all active movies"""
    return db.query(Movie).filter(Movie.is_active == 1).all()


def get_screenings_for_hall_and_date(
    db: Session, 
    hallid: str, 
    companyid: str, 
    branchid: str, 
    screening_date: date
):
    """Get all screenings for a specific hall on a specific date"""
    return db.query(Screening).filter(
        Screening.hallid == hallid,
        Screening.hallcompanyid == companyid,
        Screening.hallbranchid == branchid,
        Screening.date == screening_date
    ).order_by(Screening.starttime).all()


def calculate_revenue_for_screening(db: Session, screening_id: int):
    """Calculate total revenue for a screening"""
    total = db.query(func.sum(Booking.totalamount)).filter(
        Booking.screeningid == screening_id,
        Booking.status == 'CONFIRMED'  # Only count confirmed bookings
    ).scalar()
    
    return total or Decimal('0.00')
