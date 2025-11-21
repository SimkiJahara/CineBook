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
    eidr: str = Field(..., max_length=50)
    title: str = Field(..., max_length=255)
    posterurl: Optional[str] = Field(None, max_length=255)        # ← DB: posterurl
    lengthmin: Optional[int] = Field(None, gt=0, lt=500)          # ← DB: lengthmin
    rating: Optional[str] = Field(None, max_length=10)            # ← DB: rating
    releasedate: Optional[date] = None                            # ← DB: releasedate
    description: Optional[str] = None
    director: Optional[str] = Field(None, max_length=200)
    trailerurl: Optional[str] = Field(None, max_length=255)       # ← DB: trailerurl
    language: Optional[str] = Field('English', max_length=50)

    class Config:
        from_attributes = True


class MovieCreate(MovieBase):
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

    class Config:
        from_attributes = True


class MovieResponse(BaseModel):
    eidr: str
    title: str
    posterurl: Optional[str] = None           # ← matches DB
    lengthmin: Optional[int] = None           # ← matches DB
    rating: Optional[str] = None
    releasedate: Optional[date] = None        # ← matches DB
    description: Optional[str] = None
    director: Optional[str] = None
    trailerurl: Optional[str] = None          # ← matches DB
    language: Optional[str] = None
    genres: List[GenreResponse] = []
    cast: List[str] = []
    average_rating: float = 0.0
    review_count: int = 0

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    eidr: str
    title: str
    posterurl: Optional[str] = None
    lengthmin: Optional[int] = None
    rating: Optional[str] = None
    releasedate: Optional[date] = None
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