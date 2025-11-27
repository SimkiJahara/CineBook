from sqlalchemy.orm import Session
from app.models.location import City
from app.schemas.location import CityCreate

def create_city(db: Session, city_data: CityCreate):
    """
    Create a new city in Database
    """
    new_city = City(name=city_data.name)
    db.add(new_city)
    db.commit()
    db.refresh(new_city)
    return new_city


def get_all_cities(db: Session):
    """
    Return all cities from database
    """
    return db.query(City).all()