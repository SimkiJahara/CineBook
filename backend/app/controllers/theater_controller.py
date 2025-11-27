from sqlalchemy.orm import Session

from app.models.location import Theater
from app.schemas.location import TheaterCreate


def create_theater(db: Session, theater: TheaterCreate) :
    """
    Create and save a new theater.
    """
    new_theater = Theater(
        name=theater.name,
        description=theater.description,
        contact_email=theater.contact_email,
        contact_phone=theater.contact_phone,
        city_id=theater.city_id,
        address_id=theater.address_id,
    )
    db.add(new_theater)
    db.commit()
    db.refresh(new_theater)
    return new_theater


def get_all_theaters(db: Session):
    """
    Get all theaters from the database.
    """
    return db.query(Theater).all()
