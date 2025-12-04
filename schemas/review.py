"""Reviews schema."""

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .movie import Movie
    from .user import User


class ReviewsBase(BaseModel):
    movie_eidr: Optional[str] = None
    user_id: Optional[int] = None
    rating: Optional[Decimal] = None
    review_text: Optional[str] = None


class ReviewsCreate(ReviewsBase):
    pass


class Reviews(ReviewsBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    movie: Optional["Movie"] = None
    user: Optional["User"] = None

    model_config = ConfigDict(from_attributes=True)