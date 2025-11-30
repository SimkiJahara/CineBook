from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import ScreeningCreate, ScreeningRead
from app.controllers.screening_controller import (
    create_screening,
    get_all_screenings,
)

router = APIRouter(prefix="/screenings", tags=["Screenings"])


@router.post("/", response_model=ScreeningRead)
def create_screening_route(
    screening: ScreeningCreate,
    db: Session = Depends(get_db),
):
    return create_screening(db, screening)


@router.get("/", response_model=list[ScreeningRead])
def get_screenings_route(
    db: Session = Depends(get_db),
):
    return get_all_screenings(db)
