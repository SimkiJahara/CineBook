"""
Movie Management Service
Business logic for movie operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, timedelta, date
from typing import List, Optional

from app.models.movie import Movie, Genre, Review, movie_genre_association, movie_cast_association
from app.schemas.movie import (
    MovieCreate, MovieUpdate, MovieFilter,
    ReviewCreate, ReviewUpdate,
    GenreCreate
)

class MovieService:
    def __init__(self, db: Session):
        self.db = db

    # ========== Genre Operations ==========
    def create_genre(self, genre_data: GenreCreate):
        """Create a new genre"""
        existing = self.db.query(Genre).filter(Genre.name == genre_data.name).first()
        if existing:
            raise ValueError(f"Genre '{genre_data.name}' already exists")
        genre = Genre(**genre_data.model_dump())
        self.db.add(genre)
        self.db.commit()
        self.db.refresh(genre)
        return genre

    def get_all_genres(self) -> List[Genre]:
        """Get all genres"""
        return self.db.query(Genre).order_by(Genre.name).all()

    def get_genre_by_id(self, genre_id: int) -> Optional[Genre]:
        """Get genre by ID"""
        return self.db.query(Genre).filter(Genre.id == genre_id).first()

    # ========== Movie CRUD Operations ==========
    def create_movie(self, movie_data: MovieCreate):
        """Create a new movie"""
        existing = self.db.query(Movie).filter(Movie.eidr == movie_data.eidr).first()
        if existing:
            raise ValueError(f"Movie with EIDR '{movie_data.eidr}' already exists")

        genre_ids = movie_data.genre_ids
        cast_members = movie_data.cast
        movie_dict = movie_data.model_dump(exclude={'genre_ids', 'cast'})
        movie = Movie(**movie_dict)

        if genre_ids:
            genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            movie.genres = genres

        self.db.add(movie)
        self.db.flush()

        if cast_members:
            for cast_member in cast_members:
                self.db.execute(
                    movie_cast_association.insert().values(
                        movie_eidr=movie.eidr,
                        cast_member=cast_member
                    )
                )

        self.db.commit()
        self.db.refresh(movie)
        return movie

    def get_movie_by_eidr(self, eidr: str) -> Optional[Movie]:
        """Get movie by EIDR"""
        return self.db.query(Movie).filter(
            Movie.eidr == eidr,
            Movie.is_active == 1
        ).first()

    def get_movies(self, filters: MovieFilter) -> List[Movie]:
        """Get movies with filtering, sorting, and pagination"""
        query = self.db.query(Movie).filter(Movie.is_active == 1)

        if filters.title:
            query = query.filter(Movie.title.ilike(f"%{filters.title}%"))
        if filters.genres:
            query = query.join(Movie.genres).filter(Genre.name.in_(filters.genres))
        if filters.min_duration:
            query = query.filter(Movie.duration_min >= filters.min_duration)
        if filters.max_duration:
            query = query.filter(Movie.duration_min <= filters.max_duration)
        if filters.languages:
            query = query.filter(Movie.language.in_(filters.languages))
        if filters.age_rating:
            query = query.filter(Movie.rating == filters.age_rating)

        if filters.sort_by:
            sort_column = getattr(Movie, filters.sort_by)
            if filters.order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        query = query.offset(filters.skip).limit(filters.limit)
        return query.all()

    def update_movie(self, eidr: str, movie_update: MovieUpdate):
        """Update movie details"""
        movie = self.get_movie_by_eidr(eidr)
        if not movie:
            return None

        update_data = movie_update.model_dump(exclude_unset=True, exclude={'genre_ids', 'cast'})
        for field, value in update_data.items():
            setattr(movie, field, value)

        if movie_update.genre_ids is not None:
            genres = self.db.query(Genre).filter(Genre.id.in_(movie_update.genre_ids)).all()
            movie.genres = genres

        if movie_update.cast is not None:
            self.db.execute(
                movie_cast_association.delete().where(
                    movie_cast_association.c.movie_eidr == eidr
                )
            )
            for cast_member in movie_update.cast:
                self.db.execute(
                    movie_cast_association.insert().values(
                        movie_eidr=eidr,
                        cast_member=cast_member
                    )
                )

        movie.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(movie)
        return movie

    def delete_movie(self, eidr: str) -> bool:
        """Soft delete movie by setting is_active=0"""
        movie = self.get_movie_by_eidr(eidr)
        if not movie:
            return False
        movie.is_active = 0
        movie.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    # ========== Movie Discovery ==========
    def get_now_showing(self, limit: int = 20) -> List[Movie]:
        """Get movies showing today"""
        today = date.today()
        return self.db.query(Movie).filter(
            Movie.is_active == 1,
            Movie.release_date <= today
        ).order_by(Movie.release_date.desc()).limit(limit).all()

    def get_this_week(self, limit: int = 20) -> List[Movie]:
        """Get movies showing this week"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return self.db.query(Movie).filter(
            Movie.is_active == 1,
            Movie.release_date >= week_start,
            Movie.release_date <= week_end
        ).order_by(Movie.release_date.asc()).limit(limit).all()

    def get_coming_soon(self, limit: int = 20) -> List[Movie]:
        """Get upcoming movies (released after today)"""
        today = date.today()
        return self.db.query(Movie).filter(
            Movie.is_active == 1,
            Movie.release_date > today
        ).order_by(Movie.release_date.asc()).limit(limit).all()

    # ========== Review Operations ==========
    def create_review(self, review_data: ReviewCreate, user_id: str):
        """Create a review for a movie"""
        movie = self.get_movie_by_eidr(review_data.movie_eidr)
        if not movie:
            raise ValueError(f"Movie with EIDR '{review_data.movie_eidr}' not found")

        existing = self.db.query(Review).filter(
            Review.movie_eidr == review_data.movie_eidr,
            Review.user_id == user_id
        ).first()
        if existing:
            raise ValueError("You have already reviewed this movie")

        review = Review(
            **review_data.model_dump(),
            user_id=user_id
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_movie_reviews(self, movie_eidr: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get all reviews for a movie"""
        return self.db.query(Review).filter(
            Review.movie_eidr == movie_eidr
        ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    def update_review(self, review_id: int, review_update: ReviewUpdate, user_id: str):
        """Update a review (user can only update their own review)"""
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()
        if not review:
            return None

        update_data = review_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        review.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, review_id: int, user_id: str) -> bool:
        """Delete a review (user can only delete their own review)"""
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True