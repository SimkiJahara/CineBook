from sqlalchemy.orm import Session

from app.models.location import Hall
from app.schemas.location import HallCreate


def create_hall(db: Session, hall: HallCreate) -> Hall:
    """
    Create and save a new hall.
    """
    new_hall = Hall(
        name=hall.name,
        total_seats=hall.total_seats,
        # hall_type=hall.hall_type,
        theater_id=hall.theater_id,
    )
    db.add(new_hall)
    db.commit()
    db.refresh(new_hall)
    return new_hall


def get_all_halls(db: Session):
    """
    Get all halls.
    """
    return db.query(Hall).all()
