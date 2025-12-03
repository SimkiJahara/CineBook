"""Movie controller module for CineBook API.

Handles API endpoints for movies, genres, and reviews.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import (
    GenreCreate,
    GenreResponse,
    MovieCreate,
    MovieFilter,
    MovieListResponse,
    MovieResponse,
    MovieUpdate,
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.movie_service import MovieService
from app.utils.auth import get_current_admin, get_current_user


router = APIRouter(prefix="/api/movies", tags=["Movies"])


# Helper function to convert movie to response using Pydantic (clean & safe)
def _movie_response(movie):
    """Convert movie model to response schema.

    :param movie: Movie model instance.
    :return: MovieResponse schema.
    """
    return MovieResponse.from_orm(movie)


# ==================== Genre Endpoints ====================
@router.post("/genres", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre: GenreCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin),
):
    """Create a new genre.

    :param genre: Genre creation data.
    :param db: Database session.
    :param user: Current admin user.
    :return: Created genre response.
    """
    service = MovieService(db)
    try:
        return service.create_genre(genre)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/genres", response_model=List[GenreResponse])
async def get_all_genres(db: Session = Depends(get_db)):
    """Retrieve all genres.

    :param db: Database session.
    :return: List of genre responses.
    """
    service = MovieService(db)
    return service.get_all_genres()


# ==================== Movie CRUD Endpoints ====================
@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin),
):
    """Create a new movie.

    :param movie: Movie creation data.
    :param db: Database session.
    :param user: Current admin user.
    :return: Created movie response.
    """
    service = MovieService(db)
    try:
        created = service.create_movie(movie)
        return _movie_response(created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[MovieListResponse])
async def get_movies(
    title: Optional[str] = Query(None),
    genres: Optional[str] = Query(None),
    min_duration: Optional[int] = Query(None, ge=0),
    max_duration: Optional[int] = Query(None, le=500),
    languages: Optional[str] = Query(None),
    age_rating: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("title"),
    order: Optional[str] = Query("asc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve a list of movies with filters.

    :param title: Title filter.
    :param genres: Comma-separated genres.
    :param min_duration: Minimum duration in minutes.
    :param max_duration: Maximum duration in minutes.
    :param languages: Comma-separated languages.
    :param age_rating: Age rating filter.
    :param sort_by: Field to sort by.
    :param order: Sort order (asc/desc).
    :param skip: Number of records to skip.
    :param limit: Maximum records to return.
    :param db: Database session.
    :return: List of movie list responses.
    """
    filters = MovieFilter(
        title=title,
        genres=genres.split(",") if genres else None,
        min_duration=min_duration,
        max_duration=max_duration,
        languages=languages.split(",") if languages else None,
        age_rating=age_rating,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )
    service = MovieService(db)
    movies = service.get_movies(filters)
    return [MovieListResponse.from_orm(m) for m in movies]


@router.get("/discovery/now-showing", response_model=List[MovieListResponse])
async def get_now_showing(limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    """Retrieve currently showing movies.

    :param limit: Maximum movies to return.
    :param db: Database session.
    :return: List of movie list responses.
    """
    service = MovieService(db)
    movies = service.get_now_showing(limit)
    return [MovieListResponse.from_orm(m) for m in movies]


@router.get("/discovery/this-week", response_model=List[MovieListResponse])
async def get_this_week(limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    """Retrieve movies releasing this week.

    :param limit: Maximum movies to return.
    :param db: Database session.
    :return: List of movie list responses.
    """
    service = MovieService(db)
    movies = service.get_this_week(limit)
    return [MovieListResponse.from_orm(m) for m in movies]


@router.get("/discovery/coming-soon", response_model=List[MovieListResponse])
async def get_coming_soon(limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    """Retrieve upcoming movies.

    :param limit: Maximum movies to return.
    :param db: Database session.
    :return: List of movie list responses.
    """
    service = MovieService(db)
    movies = service.get_coming_soon(limit)
    return [MovieListResponse.from_orm(m) for m in movies]


# ==================== REVIEW ENDPOINTS - MUST COME BEFORE SINGLE MOVIE ROUTE!!! ====================
@router.post("/{eidr:path}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    eidr: str,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a review for a movie.

    :param eidr: Movie EIDR identifier.
    :param review: Review creation data.
    :param db: Database session.
    :param user: Current user.
    :return: Created review response.
    """
    if review.movie_eidr != eidr:
        raise HTTPException(status_code=400, detail="EIDR mismatch")
    service = MovieService(db)
    try:
        created = service.create_review(review, user.id)
        return ReviewResponse.from_orm(created)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{eidr:path}/reviews", response_model=List[ReviewResponse])
async def get_movie_reviews(
    eidr: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Retrieve reviews for a movie.

    :param eidr: Movie EIDR identifier.
    :param skip: Number of records to skip.
    :param limit: Maximum records to return.
    :param db: Database session.
    :return: List of review responses.
    """
    service = MovieService(db)
    reviews = service.get_movie_reviews(eidr, skip, limit)
    return [ReviewResponse.from_orm(r) for r in reviews]


# ==================== Single Movie Endpoints (EIDR with slashes) - AFTER reviews ====================
@router.get("/{eidr:path}", response_model=MovieResponse)
async def get_movie(eidr: str, db: Session = Depends(get_db)):
    """Retrieve a single movie by EIDR.

    :param eidr: Movie EIDR identifier.
    :param db: Database session.
    :return: Movie response.
    """
    service = MovieService(db)
    movie = service.get_movie_by_eidr(eidr)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie '{eidr}' not found")
    return _movie_response(movie)


@router.put("/{eidr:path}", response_model=MovieResponse)
async def update_movie(
    eidr: str,
    movie_update: MovieUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin),
):
    """Update a movie by EIDR.

    :param eidr: Movie EIDR identifier.
    :param movie_update: Movie update data.
    :param db: Database session.
    :param user: Current admin user.
    :return: Updated movie response.
    """
    service = MovieService(db)
    updated = service.update_movie(eidr, movie_update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Movie '{eidr}' not found")
    return _movie_response(updated)


@router.delete("/{eidr:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    eidr: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin),
):
    """Delete (deactivate) a movie by EIDR.

    :param eidr: Movie EIDR identifier.
    :param db: Database session.
    :param user: Current admin user.
    :return: None (204 status).
    """
    service = MovieService(db)
    if not service.delete_movie(eidr):
        raise HTTPException(status_code=404, detail=f"Movie '{eidr}' not found")
    return None


# ==================== Review Management (by review ID) ====================
@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a review by ID.

    :param review_id: Review identifier.
    :param review_update: Review update data.
    :param db: Database session.
    :param user: Current user.
    :return: Updated review response.
    """
    service = MovieService(db)
    updated = service.update_review(review_id, review_update, user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    return ReviewResponse.from_orm(updated)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Delete a review by ID.

    :param review_id: Review identifier.
    :param db: Database session.
    :param user: Current user.
    :return: None (204 status).
    """
    service = MovieService(db)
    if not service.delete_review(review_id, user.id):
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    return None