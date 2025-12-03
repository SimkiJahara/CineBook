from fastapi import APIRouter, FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
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

# Import helper functions from services
from services.screening_service import (
    get_owner_theaters_and_halls,
    get_active_movies,
    get_screenings_for_hall_and_date,
    calculate_revenue_for_screening
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Landing page"""
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )


@router.get("/dashboard/{owner_id}", response_class=HTMLResponse)
def owner_dashboard(
    request: Request, 
    owner_id: int, 
    db: Session = Depends(get_db)
):
    """Theater owner dashboard with navigation buttons"""
    owner = db.query(Theaterowner).filter(Theaterowner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request, 
            "owner": owner,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Schedule screening form page
# ---------------------------------------------------------------
@router.get("/schedule-screening/{owner_id}", response_class=HTMLResponse)
def schedule_screening_page(
    request: Request,
    owner_id: int,
    hallid: Optional[str] = None,
    companyid: Optional[str] = None,
    branchid: Optional[str] = None,
    screening_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Display the screening scheduling form"""
    theaters, halls = get_owner_theaters_and_halls(db, owner_id)
    movies = get_active_movies(db)
    
    existing_screenings = []
    parsed_date = None
    selected_hall = None
    
    # If hall and date are selected, show existing screenings for that slot
    if hallid and companyid and branchid and screening_date:
        try:
            parsed_date = datetime.strptime(screening_date, "%Y-%m-%d").date()
            existing_screenings = get_screenings_for_hall_and_date(
                db, hallid, companyid, branchid, parsed_date
            )
            selected_hall = db.query(Hall).filter(
                Hall.hallid == hallid,
                Hall.companyid == companyid,
                Hall.branchid == branchid
            ).first()
        except ValueError:
            pass  # Invalid date format
    
    return templates.TemplateResponse(
        "schedule_screening.html",
        {
            "request": request,
            "owner_id": owner_id,
            "theaters": theaters,
            "halls": halls,
            "movies": movies,
            "existing_screenings": existing_screenings,
            "selected_hall": selected_hall,
            "selected_date": parsed_date,
            "selected_hallid": hallid,
            "selected_companyid": companyid,
            "selected_branchid": branchid
        }
    )

# ---------------------------------------------------------------
# Save scheduled screening
# ---------------------------------------------------------------
@router.post("/screening-scheduled/{owner_id}", response_class=HTMLResponse)
async def screening_scheduled(
    request: Request,
    owner_id: int,
    db: Session = Depends(get_db),
    movieeidr: str = Form(...),
    hallid: str = Form(...),
    hallcompanyid: str = Form(...),
    hallbranchid: str = Form(...),
    date: str = Form(...),
    starttime: str = Form(...)
):
    """Create a new screening (unpublished by default)"""
    
    # Verify the hall belongs to the owner
    hall = db.query(Hall).filter(
        Hall.hallid == hallid,
        Hall.companyid == hallcompanyid,
        Hall.branchid == hallbranchid
    ).first()
    
    if not hall:
        raise HTTPException(status_code=404, detail="Hall not found")
    
    # Verify the theater belongs to the owner
    theater = db.query(Theater).filter(
        Theater.companyid == hallcompanyid,
        Theater.branchid == hallbranchid,
        Theater.ownerid == owner_id
    ).first()
    
    if not theater:
        raise HTTPException(
            status_code=403, 
            detail="You don't have permission to schedule screenings for this hall"
        )
    
    # Parse date and time
    try:
        screening_date = datetime.strptime(date, "%Y-%m-%d").date()
        screening_time = datetime.strptime(starttime, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    # Check if movie exists and is active
    movie = db.query(Movie).filter(
        Movie.eidr == movieeidr,
        Movie.is_active == 1
    ).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found or inactive")
    
    # Check for time conflicts
    existing = db.query(Screening).filter(
        Screening.hallid == hallid,
        Screening.hallcompanyid == hallcompanyid,
        Screening.hallbranchid == hallbranchid,
        Screening.date == screening_date,
        Screening.starttime == screening_time
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="A screening already exists at this time"
        )
    
    # Create new screening (unpublished by default)
    new_screening = Screening(
        date=screening_date,
        starttime=screening_time,
        status='SCHEDULED',
        movieeidr=movieeidr,
        hallid=hallid,
        hallcompanyid=hallcompanyid,
        hallbranchid=hallbranchid
    )
    
    db.add(new_screening)
    db.commit()
    db.refresh(new_screening)
    
    return templates.TemplateResponse(
        "schedule_confirmation.html",
        {
            "request": request, 
            "screening": new_screening,
            "movie": movie,
            "hall": hall,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Unpublished screenings
# ---------------------------------------------------------------
@router.get("/unpublished-screenings/{owner_id}", response_class=HTMLResponse)
def unpublished_screenings(
    request: Request,
    owner_id: int,
    date_filter: Optional[str] = None,
    hallid: Optional[str] = None,
    movieeidr: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """View all unpublished screenings with filters"""
    
    theaters, halls = get_owner_theaters_and_halls(db, owner_id)
    movies = get_active_movies(db)
    
    # Get hall IDs that belong to this owner
    owner_hall_keys = [
        (h.hallid, h.companyid, h.branchid) for h in halls
    ]
    
    # Base query: unpublished screenings in owner's halls
    query = db.query(Screening).filter(
        Screening.status == 'SCHEDULED'  # Unpublished status
    )
    
    # Filter by owner's halls
    hall_filters = []
    for hallid_key, companyid_key, branchid_key in owner_hall_keys:
        hall_filters.append(
            (Screening.hallid == hallid_key) &
            (Screening.hallcompanyid == companyid_key) &
            (Screening.hallbranchid == branchid_key)
        )
    
    if hall_filters:
        from sqlalchemy import or_
        query = query.filter(or_(*hall_filters))
    
    # Apply filters
    if hallid:
        query = query.filter(Screening.hallid == hallid)
    
    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            query = query.filter(Screening.date == filter_date)
        except ValueError:
            pass
    
    if movieeidr:
        query = query.filter(Screening.movieeidr == movieeidr)
    
    screenings = query.order_by(
        Screening.date, 
        Screening.hallid, 
        Screening.starttime
    ).all()
    
    # Group by date, then by hall
    screenings_by_date: Dict[str, Dict[str, List[Screening]]] = {}
    
    for screening in screenings:
        date_str = str(screening.date)
        hall_key = f"{screening.hallid}-{screening.hallcompanyid}-{screening.hallbranchid}"
        
        if date_str not in screenings_by_date:
            screenings_by_date[date_str] = {}
        
        if hall_key not in screenings_by_date[date_str]:
            screenings_by_date[date_str][hall_key] = []
        
        screenings_by_date[date_str][hall_key].append(screening)
    
    return templates.TemplateResponse(
        "unpublished_list.html",
        {
            "request": request,
            "owner_id": owner_id,
            "theaters": theaters,
            "halls": halls,
            "movies": movies,
            "screenings_by_date": screenings_by_date,
            "current_date": date.today()
        }
    )

# ---------------------------------------------------------------
# Published screenings (future)
# ---------------------------------------------------------------
@router.get("/published-screenings/{owner_id}", response_class=HTMLResponse)
def published_screenings(
    request: Request,
    owner_id: int,
    date_filter: Optional[str] = None,
    hallid: Optional[str] = None,
    movieeidr: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """View all published future screenings with filters"""
    
    theaters, halls = get_owner_theaters_and_halls(db, owner_id)
    movies = get_active_movies(db)
    
    # Get hall IDs that belong to this owner
    owner_hall_keys = [
        (h.hallid, h.companyid, h.branchid) for h in halls
    ]
    
    today = date.today()
    
    # Base query: published screenings in owner's halls, future dates only
    query = db.query(Screening).filter(
        Screening.status == 'PUBLISHED',
        Screening.date >= today
    )
    
    # Filter by owner's halls
    hall_filters = []
    for hallid_key, companyid_key, branchid_key in owner_hall_keys:
        hall_filters.append(
            (Screening.hallid == hallid_key) &
            (Screening.hallcompanyid == companyid_key) &
            (Screening.hallbranchid == branchid_key)
        )
    
    if hall_filters:
        from sqlalchemy import or_
        query = query.filter(or_(*hall_filters))
    
    # Apply filters
    if hallid:
        query = query.filter(Screening.hallid == hallid)
    
    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            query = query.filter(Screening.date == filter_date)
        except ValueError:
            pass
    
    if movieeidr:
        query = query.filter(Screening.movieeidr == movieeidr)
    
    screenings = query.order_by(
        Screening.date,
        Screening.hallid,
        Screening.starttime
    ).all()
    
    # Group by date, then by hall
    screenings_by_date: Dict[str, Dict[str, List[Screening]]] = {}
    
    for screening in screenings:
        date_str = str(screening.date)
        hall_key = f"{screening.hallid}-{screening.hallcompanyid}-{screening.hallbranchid}"
        
        if date_str not in screenings_by_date:
            screenings_by_date[date_str] = {}
        
        if hall_key not in screenings_by_date[date_str]:
            screenings_by_date[date_str][hall_key] = []
        
        screenings_by_date[date_str][hall_key].append(screening)
    
    return templates.TemplateResponse(
        "published_list.html",
        {
            "request": request,
            "owner_id": owner_id,
            "theaters": theaters,
            "halls": halls,
            "movies": movies,
            "screenings_by_date": screenings_by_date,
            "current_date": today
        }
    )

# ---------------------------------------------------------------
# Past screenings
# ---------------------------------------------------------------
@router.get("/past-screenings/{owner_id}", response_class=HTMLResponse)
def past_screenings(
    request: Request,
    owner_id: int,
    date_filter: Optional[str] = None,
    hallid: Optional[str] = None,
    movieeidr: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """View all past screenings with revenue data"""
    
    theaters, halls = get_owner_theaters_and_halls(db, owner_id)
    movies = get_active_movies(db)
    
    # Get hall IDs that belong to this owner
    owner_hall_keys = [
        (h.hallid, h.companyid, h.branchid) for h in halls
    ]
    
    today = date.today()
    
    # Base query: past screenings (date < today)
    query = db.query(Screening).filter(
        Screening.date < today
    )
    
    # Filter by owner's halls
    hall_filters = []
    for hallid_key, companyid_key, branchid_key in owner_hall_keys:
        hall_filters.append(
            (Screening.hallid == hallid_key) &
            (Screening.hallcompanyid == companyid_key) &
            (Screening.hallbranchid == branchid_key)
        )
    
    if hall_filters:
        from sqlalchemy import or_
        query = query.filter(or_(*hall_filters))
    
    # Apply filters
    if hallid:
        query = query.filter(Screening.hallid == hallid)
    
    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            query = query.filter(Screening.date == filter_date)
        except ValueError:
            pass
    
    if movieeidr:
        query = query.filter(Screening.movieeidr == movieeidr)
    
    screenings = query.order_by(
        Screening.date.desc(),
        Screening.hallid,
        Screening.starttime
    ).all()
    
    # Calculate revenue for each screening
    screenings_with_revenue = []
    for screening in screenings:
        revenue = calculate_revenue_for_screening(db, screening.id)
        screenings_with_revenue.append({
            'screening': screening,
            'revenue': revenue
        })
    
    # Group by date, then by hall
    screenings_by_date: Dict[str, Dict[str, List[dict]]] = {}
    
    for item in screenings_with_revenue:
        screening = item['screening']
        date_str = str(screening.date)
        hall_key = f"{screening.hallid}-{screening.hallcompanyid}-{screening.hallbranchid}"
        
        if date_str not in screenings_by_date:
            screenings_by_date[date_str] = {}
        
        if hall_key not in screenings_by_date[date_str]:
            screenings_by_date[date_str][hall_key] = []
        
        screenings_by_date[date_str][hall_key].append(item)
    
    return templates.TemplateResponse(
        "past_list.html",
        {
            "request": request,
            "owner_id": owner_id,
            "theaters": theaters,
            "halls": halls,
            "movies": movies,
            "screenings_by_date": screenings_by_date
        }
    )

# ---------------------------------------------------------------
# Edit screening page
# ---------------------------------------------------------------
@router.get("/edit-screening/{screening_id}", response_class=HTMLResponse)
def edit_screening_page(
    request: Request, 
    screening_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Display edit form for a screening"""
    
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(404, "Screening not found")

    if screening.status == 'PUBLISHED':
        raise HTTPException(404, "Screening has already been published. No further changes can be made.")
    
    # Verify ownership
    theater = db.query(Theater).filter(
        Theater.companyid == screening.hallcompanyid,
        Theater.branchid == screening.hallbranchid
    ).first()
    
    if not theater or theater.ownerid != owner_id:
        raise HTTPException(403, "You don't have permission to edit this screening")
    
    movies = get_active_movies(db)
    hall = db.query(Hall).filter(
        Hall.hallid == screening.hallid,
        Hall.companyid == screening.hallcompanyid,
        Hall.branchid == screening.hallbranchid
    ).first()
    
    return templates.TemplateResponse(
        "edit_screening.html",
        {
            "request": request,
            "screening": screening,
            "movies": movies,
            "hall": hall,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Edit confirmation
# ---------------------------------------------------------------
@router.post("/screening-edited/{screening_id}", response_class=HTMLResponse)
async def edit_screening(
    request: Request,
    screening_id: int,
    owner_id: int,
    db: Session = Depends(get_db),
    movieeidr: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    starttime: Optional[str] = Form(None)
):
    """Update screening information"""
    
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(404, "Screening not found")
    
    if screening.status == 'PUBLISHED':
        raise HTTPException(404, "Screening has already been published. No further changes can be made.")

    # Verify ownership
    theater = db.query(Theater).filter(
        Theater.companyid == screening.hallcompanyid,
        Theater.branchid == screening.hallbranchid
    ).first()
    
    if not theater or theater.ownerid != owner_id:
        raise HTTPException(403, "You don't have permission to edit this screening")
    
    # Update fields if provided
    if movieeidr:
        movie = db.query(Movie).filter(
            Movie.eidr == movieeidr,
            Movie.is_active == 1
        ).first()
        if movie:
            screening.movieeidr = movieeidr
    
    if date:
        try:
            screening.date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    if starttime:
        try:
            screening.starttime = datetime.strptime(starttime, "%H:%M").time()
        except ValueError:
            pass
    
    db.commit()
    db.refresh(screening)
    
    return templates.TemplateResponse(
        "edit_confirmation.html",
        {
            "request": request,
            "screening": screening,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Publish screening page
# ---------------------------------------------------------------
@router.get("/publish-screening/{screening_id}", response_class=HTMLResponse)
def publish_screening_page(
    request: Request,
    screening_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Display publish confirmation page"""
    
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(404, "Screening not found")

    if screening.status == 'PUBLISHED':
        raise HTTPException(404, "This screening already exists.")
    
    # Verify ownership
    theater = db.query(Theater).filter(
        Theater.companyid == screening.hallcompanyid,
        Theater.branchid == screening.hallbranchid
    ).first()
    
    if not theater or theater.ownerid != owner_id:
        raise HTTPException(403, "You don't have permission to publish this screening")
    
    return templates.TemplateResponse(
        "publish_screening.html",
        {
            "request": request,
            "screening": screening,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Publish confirmation
# ---------------------------------------------------------------
@router.post("/screening-published/{screening_id}", response_class=HTMLResponse)
def publish_screening(
    request: Request,
    screening_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Publish a screening"""
    
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(404, "Screening not found")
    
    if screening.status == 'PUBLISHED':
        raise HTTPException(404, "This screening already exists.")
    
    # Verify ownership
    theater = db.query(Theater).filter(
        Theater.companyid == screening.hallcompanyid,
        Theater.branchid == screening.hallbranchid
    ).first()
    
    if not theater or theater.ownerid != owner_id:
        raise HTTPException(403, "You don't have permission to publish this screening")
    
    screening.status = 'PUBLISHED'
    db.commit()
    db.refresh(screening)
    
    return templates.TemplateResponse(
        "publish_confirmation.html",
        {
            "request": request,
            "screening": screening,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Delete screening page
# ---------------------------------------------------------------
@router.get("/delete-screening/{screening_id}", response_class=HTMLResponse)
def delete_screening_page(
    request: Request,
    screening_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Display delete confirmation page"""
    
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(404, "Screening not found")

    if screening.status == 'PUBLISHED':
        raise HTTPException(404, "You cannot delete a published screening.")
    
    # Verify ownership
    theater = db.query(Theater).filter(
        Theater.companyid == screening.hallcompanyid,
        Theater.branchid == screening.hallbranchid
    ).first()
    
    if not theater or theater.ownerid != owner_id:
        raise HTTPException(403, "You don't have permission to delete this screening")
    
    # Check if there are any bookings
    has_bookings = db.query(Booking).filter(
        Booking.screeningid == screening_id
    ).first() is not None
    
    return templates.TemplateResponse(
        "delete_screening.html",
        {
            "request": request,
            "screening": screening,
            "has_bookings": has_bookings,
            "owner_id": owner_id
        }
    )

# ---------------------------------------------------------------
# Delete confirmation
# ---------------------------------------------------------------
@router.post("/screening-deleted/{screening_id}", response_class=HTMLResponse)
def delete_screening(
    request: Request,
    screening_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Delete a screening"""
    
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(404, "Screening not found")

    if screening.status == 'PUBLISHED':
        raise HTTPException(404, "You cannot delete a published screening.")
    
    # Verify ownership
    theater = db.query(Theater).filter(
        Theater.companyid == screening.hallcompanyid,
        Theater.branchid == screening.hallbranchid
    ).first()
    
    if not theater or theater.ownerid != owner_id:
        raise HTTPException(403, "You don't have permission to delete this screening")
    
    # Check if there are any confirmed bookings
    has_confirmed_bookings = db.query(Booking).filter(
        Booking.screeningid == screening_id,
        Booking.status == 'CONFIRMED'
    ).first() is not None
    
    if has_confirmed_bookings:
        raise HTTPException(
            400,
            "Cannot delete screening with confirmed bookings"
        )
    
    db.delete(screening)
    db.commit()
    
    return templates.TemplateResponse(
        "delete_confirmation.html",
        {
            "request": request,
            "screening_id": screening_id,
            "owner_id": owner_id
        }
    )
