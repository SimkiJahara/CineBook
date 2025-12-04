from .user import (
    UserBase, UserCreate, User,
    BuyerBase, BuyerCreate, Buyer,
    SuperadminBase, SuperadminCreate, Superadmin,
    TheaterownerBase, TheaterownerCreate, Theaterowner
)
from .movie import (
    GenresBase, GenresCreate, Genres,
    MovieBase, MovieCreate, Movie,
    MovieCastBase, MovieCastCreate, MovieCast
)
from .theater import (
    TheaterBase, TheaterCreate, Theater,
    HallBase, HallCreate, Hall,
    SeatlayoutBase, SeatlayoutCreate, Seatlayout,
    SeatBase, SeatCreate, Seat
)
from .screening import ScreeningBase, ScreeningCreate, Screening
from .booking import BookingBase, BookingCreate, Booking
from .promocode import PromocodeBase, PromocodeCreate, Promocode
from .review import ReviewsBase, ReviewsCreate, Reviews
from .screening_draft import ScreeningdraftBase, ScreeningdraftCreate, Screeningdraft

# Rebuild models to resolve forward references
def rebuild_models():
    """Rebuild all models to resolve forward references after all imports."""
    Buyer.model_rebuild()
    Superadmin.model_rebuild()
    Theaterowner.model_rebuild()
    Genres.model_rebuild()
    Movie.model_rebuild()
    MovieCast.model_rebuild()
    Reviews.model_rebuild()
    Promocode.model_rebuild()
    Screeningdraft.model_rebuild()
    Theater.model_rebuild()
    Hall.model_rebuild()
    Screening.model_rebuild()
    Seatlayout.model_rebuild()
    Booking.model_rebuild()
    Seat.model_rebuild()

# Call rebuild after all imports
rebuild_models()

# Export all schemas
__all__ = [
    # User schemas
    'UserBase', 'UserCreate', 'User',
    'BuyerBase', 'BuyerCreate', 'Buyer',
    'SuperadminBase', 'SuperadminCreate', 'Superadmin',
    'TheaterownerBase', 'TheaterownerCreate', 'Theaterowner',
    # Movie schemas
    'GenresBase', 'GenresCreate', 'Genres',
    'MovieBase', 'MovieCreate', 'Movie',
    'MovieCastBase', 'MovieCastCreate', 'MovieCast',
    # Theater schemas
    'TheaterBase', 'TheaterCreate', 'Theater',
    'HallBase', 'HallCreate', 'Hall',
    'SeatlayoutBase', 'SeatlayoutCreate', 'Seatlayout',
    'SeatBase', 'SeatCreate', 'Seat',
    # Screening schema
    'ScreeningBase', 'ScreeningCreate', 'Screening',
    # Booking schema
    'BookingBase', 'BookingCreate', 'Booking',
    # Promocode schema
    'PromocodeBase', 'PromocodeCreate', 'Promocode',
    # Review schema
    'ReviewsBase', 'ReviewsCreate', 'Reviews',
    # Screening draft schema
    'ScreeningdraftBase', 'ScreeningdraftCreate', 'Screeningdraft',
]
