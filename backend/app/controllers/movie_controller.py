"""
Movie Management Controller
FastAPI routes for movie CRUD operations and discovery
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.movie_service import MovieService
from app.schemas.movie import (
    MovieCreate, MovieUpdate, MovieResponse, MovieListResponse, MovieFilter,
    ReviewCreate, ReviewUpdate, ReviewResponse,
    GenreCreate, GenreResponse
)
from app.utils.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/movies", tags=["Movies"])

# ========== Genre Endpoints ==========
@router.post("/genres", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre: GenreCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Create a new genre (Admin only)"""
    service = MovieService(db)
    return service.create_genre(genre)

@router.get("/genres", response_model=List[GenreResponse])
async def get_all_genres(db: Session = Depends(get_db)):
    """Get all genres - Public endpoint"""
    service = MovieService(db)
    return service.get_all_genres()

# ========== Movie CRUD Endpoints ==========
@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Create a new movie (Admin only)"""
    service = MovieService(db)
    return service.create_movie(movie)

@router.get("/", response_model=List[MovieListResponse])
async def get_movies(
    title: Optional[str] = Query(None, description="Filter by title (partial match)"),
    genres: Optional[str] = Query(None, description="Filter by genres (comma-separated)"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum duration in minutes"),
    max_duration: Optional[int] = Query(None, le=500, description="Maximum duration in minutes"),
    languages: Optional[str] = Query(None, description="Filter by languages (comma-separated)"),
    age_rating: Optional[str] = Query(None, description="Filter by age rating"),
    sort_by: Optional[str] = Query("title", regex="^(title|release_date|rating|duration)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of movies with filtering, sorting, and pagination
    Public endpoint - No authentication required
    """
    # Build filter object
    filter_obj = MovieFilter(
        title=title,
        genres=genres.split(',') if genres else None,
        min_duration=min_duration,
        max_duration=max_duration,
        languages=languages.split(',') if languages else None,
        age_rating=age_rating,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit
    )
    service = MovieService(db)
    return service.get_movies(filter_obj)

@router.get("/{eidr}", response_model=MovieResponse)
async def get_movie(eidr: str, db: Session = Depends(get_db)):
    """Get single movie details by EIDR - Public endpoint"""
    service = MovieService(db)
    movie = service.get_movie_by_eidr(eidr)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with EIDR '{eidr}' not found"
        )
    return movie

@router.put("/{eidr}", response_model=MovieResponse)
async def update_movie(
    eidr: str,
    movie_update: MovieUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Update movie details (Admin only)"""
    service = MovieService(db)
    updated_movie = service.update_movie(eidr, movie_update)
    if not updated_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with EIDR '{eidr}' not found"
        )
    return updated_movie

@router.delete("/{eidr}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    eidr: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Delete movie (Admin only) - Soft delete by setting is_active=0"""
    service = MovieService(db)
    success = service.delete_movie(eidr)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with EIDR '{eidr}' not found"
        )

# ========== Movie Discovery Endpoints ==========
@router.get("/discovery/now-showing", response_model=List[MovieListResponse])
async def get_now_showing(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50)
):
    """Get movies showing today - Public endpoint"""
    service = MovieService(db)
    return service.get_now_showing(limit)

@router.get("/discovery/this-week", response_model=List[MovieListResponse])
async def get_this_week(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50)
):
    """Get movies showing this week - Public endpoint"""
    service = MovieService(db)
    return service.get_this_week(limit)

@router.get("/discovery/coming-soon", response_model=List[MovieListResponse])
async def get_coming_soon(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50)
):
    """Get upcoming movies - Public endpoint"""
    service = MovieService(db)
    return service.get_coming_soon(limit)

# ========== Review Endpoints ==========
@router.post("/{eidr}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    eidr: str,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit a review for a movie (Requires authentication)"""
    if review.movie_eidr != eidr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie EIDR in path does not match request body"
        )
    service = MovieService(db)
    return service.create_review(review, current_user.id)

@router.get("/{eidr}/reviews", response_model=List[ReviewResponse])
async def get_movie_reviews(
    eidr: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get all reviews for a movie - Public endpoint"""
    service = MovieService(db)
    return service.get_movie_reviews(eidr, skip, limit)

@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user's own review"""
    service = MovieService(db)
    updated_review = service.update_review(review_id, review_update, current_user.id)
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or you don't have permission to update it"
        )
    return updated_review

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete user's own review"""
    service = MovieService(db)
    success = service.delete_review(review_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or you don't have permission to delete it"
        )