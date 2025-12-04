"""Movie-related schemas."""

from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .review import Reviews
    from .screening import Screening


class GenresBase(BaseModel):
    name: str
    description: Optional[str] = None


class GenresCreate(GenresBase):
    pass


class Genres(GenresBase):
    id: int
    created_at: Optional[datetime] = None
    movie: Optional[List["Movie"]] = []

    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    eidr: str
    title: str
    posterurl: Optional[str] = None
    lengthmin: Optional[int] = None
    rating: Optional[str] = None
    releasedate: Optional[date] = None
    description: Optional[str] = None
    director: Optional[str] = None
    trailerurl: Optional[str] = None
    language: Optional[str] = "English"
    is_active: Optional[int] = 1


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    created_at: Optional[datetime] = None
    genre: Optional[List[Genres]] = []
    movie_cast: Optional[List["MovieCast"]] = []
    reviews: Optional[List["Reviews"]] = []
    screening: Optional[List["Screening"]] = []

    model_config = ConfigDict(from_attributes=True)


class MovieCastBase(BaseModel):
    cast_member: str
    movie_eidr: Optional[str] = None


class MovieCastCreate(MovieCastBase):
    pass


class MovieCast(MovieCastBase):
    id: int
    movie: Optional[Movie] = None

    model_config = ConfigDict(from_attributes=True)