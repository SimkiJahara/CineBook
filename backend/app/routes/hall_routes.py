from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import HallCreate, HallRead
from app.controllers.hall_controller import create_hall, get_all_halls

router = APIRouter(prefix="/halls", tags=["Halls"])


@router.post("/", response_model=HallRead)
def create_hall_route(hall: HallCreate, db: Session = Depends(get_db)):
    return create_hall(db, hall)


@router.get("/", response_model=list[HallRead])
def get_halls_route(db: Session = Depends(get_db)):
    return get_all_halls(db)
