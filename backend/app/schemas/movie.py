"""
Movie Schemas - Pydantic validation models
Request/Response validation for API
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# ==================== Genre Schemas ====================
class GenreBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None


class GenreCreate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Movie Schemas ====================
class MovieBase(BaseModel):
    title: str = Field(..., max_length=255)
    posterurl: Optional[str] = Field(None, max_length=255)
    lengthmin: Optional[int] = Field(None, gt=0, lt=500)
    rating: Optional[str] = Field(None, max_length=10)
    releasedate: Optional[date] = None
    description: Optional[str] = None
    director: Optional[str] = Field(None, max_length=200)
    trailerurl: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field('English', max_length=50)


class MovieCreate(MovieBase):
    eidr: str = Field(..., max_length=50)
    genre_ids: List[int] = Field(default_factory=list)
    cast: List[str] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    posterurl: Optional[str] = Field(None, max_length=255)
    lengthmin: Optional[int] = Field(None, gt=0, lt=500)
    rating: Optional[str] = Field(None, max_length=10)
    releasedate: Optional[date] = None
    description: Optional[str] = None
    director: Optional[str] = Field(None, max_length=200)
    trailerurl: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field(None, max_length=50)
    genre_ids: Optional[List[int]] = None
    cast: Optional[List[str]] = None
    is_active: Optional[int] = Field(None, ge=0, le=1)


class MovieResponse(BaseModel):
    eidr: str
    title: str
    poster_url: Optional[str] = None
    duration_min: Optional[int] = None
    rating: Optional[str] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    director: Optional[str] = None
    trailer_url: Optional[str] = None
    language: Optional[str] = None
    genres: List[GenreResponse] = []
    cast: List[str] = []
    average_rating: float = 0.0
    review_count: int = 0
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_model(cls, movie):
        """Convert SQLAlchemy model to response schema"""
        return cls(
            eidr=movie.eidr,
            title=movie.title,
            poster_url=movie.posterurl,
            duration_min=movie.lengthmin,
            rating=movie.rating,
            release_date=movie.releasedate,
            description=movie.description,
            director=movie.director,
            trailer_url=movie.trailerurl,
            language=movie.language,
            genres=[GenreResponse.model_validate(g) for g in movie.genres],
            cast=movie.cast,
            average_rating=movie.average_rating,
            review_count=movie.review_count
        )


class MovieListResponse(BaseModel):
    eidr: str
    title: str
    poster_url: Optional[str] = None
    duration_min: Optional[int] = None
    rating: Optional[str] = None
    release_date: Optional[date] = None
    language: Optional[str] = None
    genres: List[GenreResponse] = []
    average_rating: float = 0.0
    review_count: int = 0
    
    class Config:
        from_attributes = True


# ==================== Filter Schema ====================
class MovieFilter(BaseModel):
    title: Optional[str] = None
    genres: Optional[List[str]] = None
    min_duration: Optional[int] = Field(None, ge=0)
    max_duration: Optional[int] = Field(None, le=500)
    languages: Optional[List[str]] = None
    age_rating: Optional[str] = None
    sort_by: Optional[str] = Field("title")
    order: Optional[str] = Field("asc")
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


# ==================== Review Schemas ====================
class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0)
    review_text: Optional[str] = None


class ReviewCreate(ReviewBase):
    movie_eidr: str = Field(..., max_length=50)


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    review_text: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: int
    movie_eidr: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True