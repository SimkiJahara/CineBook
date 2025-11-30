from sqlalchemy.orm import Session

from app.models.location import Screening
from app.schemas.location import ScreeningCreate


def create_screening(db: Session, screening: ScreeningCreate) -> Screening:
    """
    Create and save a new screening.
    """
    new_screening = Screening(
        movie_id=screening.movie_id,
        hall_id=screening.hall_id,
        show_date=screening.show_date,
        start_time=screening.start_time,
        end_time=screening.end_time,        # can be None
        base_price=screening.base_price,
        # created_at will be set automatically by default=datetime.utcnow
    )
    db.add(new_screening)
    db.commit()
    db.refresh(new_screening)
    return new_screening


def get_all_screenings(db: Session):
    """
    Get all screenings from the database.
    """
    return db.query(Screening).all()
