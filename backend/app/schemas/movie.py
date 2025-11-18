"""
Movie Management Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime


# ========== Genre Schemas ==========
class GenreBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None


class GenreCreate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Movie Schemas ==========
class MovieBase(BaseModel):
    title: str = Field(..., max_length=200)
    poster_url: Optional[str] = Field(None, max_length=500)
    language: str = Field(..., max_length=50)
    duration_min: int = Field(..., gt=0, lt=500)
    rating: Optional[str] = Field(None, max_length=10)
    release_date: date
    description: Optional[str] = None
    director: Optional[str] = Field(None, max_length=200)
    trailer_url: Optional[str] = Field(None, max_length=500)


class MovieCreate(MovieBase):
    eidr: str = Field(..., max_length=50)
    genre_ids: List[int] = Field(default_factory=list)
    cast: List[str] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    poster_url: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=50)
    duration_min: Optional[int] = Field(None, gt=0, lt=500)
    rating: Optional[str] = Field(None, max_length=10)
    release_date: Optional[date] = None
    description: Optional[str] = None
    director: Optional[str] = Field(None, max_length=200)
    trailer_url: Optional[str] = Field(None, max_length=500)
    genre_ids: Optional[List[int]] = None
    cast: Optional[List[str]] = None
    is_active: Optional[int] = Field(None, ge=0, le=1)


class MovieResponse(MovieBase):
    eidr: str
    created_at: datetime
    updated_at: datetime
    is_active: int
    genres: List[GenreResponse] = []
    cast: List[str] = []
    average_rating: float
    review_count: int
    
    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    eidr: str
    title: str
    poster_url: Optional[str]
    language: str
    duration_min: int
    rating: Optional[str]
    release_date: date
    genres: List[GenreResponse] = []
    average_rating: float
    review_count: int
    
    class Config:
        from_attributes = True


# ========== Movie Filter Schema ==========
class MovieFilter(BaseModel):
    title: Optional[str] = None
    genres: Optional[List[str]] = None
    min_duration: Optional[int] = Field(None, ge=0)
    max_duration: Optional[int] = Field(None, le=500)
    languages: Optional[List[str]] = None
    age_rating: Optional[str] = None
    sort_by: Optional[str] = Field(None, pattern="^(title|release_date|rating|duration)$")
    order: Optional[str] = Field("asc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


# ========== Review Schemas ==========
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
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== Movie Request Schema ==========
class MovieRequestCreate(BaseModel):
    eidr: str = Field(..., max_length=50)
    requested_by: str = Field(..., max_length=50)  # User ID
    notes: Optional[str] = None


class MovieRequestResponse(BaseModel):
    id: int
    eidr: str
    requested_by: str
    status: str  # pending, approved, rejected
    notes: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True