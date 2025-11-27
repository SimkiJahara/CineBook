from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import TheaterCreate, TheaterRead
from app.controllers.theater_controller import (
    create_theater,
    get_all_theaters,
)

router = APIRouter(prefix="/theaters", tags=["Theaters"])


@router.post("/", response_model=TheaterRead)
def create_theater_route(
    theater: TheaterCreate,
    db: Session = Depends(get_db),
):
    return create_theater(db, theater)


@router.get("/", response_model=list[TheaterRead])
def get_theaters_route(
    db: Session = Depends(get_db),
):
    return get_all_theaters(db)
