from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import CityCreate, CityRead
from app.controllers.city_controller import create_city, get_all_cities

router = APIRouter(prefix="/cities",tags=["Cities"])

@router.post("/",response_model=CityRead)
def create_city_route(city:CityCreate, db: Session = Depends(get_db)):
    return create_city(db,city)

@router.get("/",response_model=list[CityRead])
def get_cities_route(db: Session = Depends(get_db)):
    return get_all_cities(db)

