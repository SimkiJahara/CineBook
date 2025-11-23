"""
Movie Service - Business logic layer
Handles all movie-related database operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, timedelta, date
from typing import List, Optional

from app.models.movie import Movie, Genre, Review, MovieCast, movie_genre_association
from app.schemas.movie import (
    MovieCreate, MovieUpdate, MovieFilter,
    ReviewCreate, ReviewUpdate, GenreCreate
)


class MovieService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== Genre Operations ====================
    def create_genre(self, genre_data: GenreCreate) -> Genre:
        existing = self.db.query(Genre).filter(Genre.name == genre_data.name).first()
        if existing:
            raise ValueError(f"Genre '{genre_data.name}' already exists")
        genre = Genre(**genre_data.model_dump())
        self.db.add(genre)
        self.db.commit()
        self.db.refresh(genre)
        return genre

    def get_all_genres(self) -> List[Genre]:
        return self.db.query(Genre).order_by(Genre.name).all()

    def get_genre_by_id(self, genre_id: int) -> Optional[Genre]:
        return self.db.query(Genre).filter(Genre.id == genre_id).first()

    # ==================== Movie CRUD ====================
    def create_movie(self, movie_data: MovieCreate) -> Movie:
        existing = self.db.query(Movie).filter(Movie.eidr == movie_data.eidr).first()
        if existing:
            raise ValueError(f"Movie with EIDR '{movie_data.eidr}' already exists")

        genre_ids = movie_data.genre_ids
        cast_list = movie_data.cast

        movie = Movie(
            eidr=movie_data.eidr,
            title=movie_data.title,
            posterurl=movie_data.posterurl,
            lengthmin=movie_data.lengthmin,
            rating=movie_data.rating,
            releasedate=movie_data.releasedate,
            description=movie_data.description,
            director=movie_data.director,
            trailerurl=movie_data.trailerurl,
            language=movie_data.language,
            is_active=1
        )

        if genre_ids:
            genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            movie.genres = genres

        self.db.add(movie)
        self.db.flush()

        for cast_member in cast_list:
            mc = MovieCast(movie_eidr=movie.eidr, cast_member=cast_member)
            self.db.add(mc)

        self.db.commit()
        self.db.refresh(movie)
        return movie

    def get_movie_by_eidr(self, eidr: str) -> Optional[Movie]:
        return self.db.query(Movie).filter(Movie.eidr == eidr).first()

    def get_movies(self, filters: MovieFilter) -> List[Movie]:
        query = self.db.query(Movie).filter(Movie.is_active == 1)

        if filters.title:
            query = query.filter(Movie.title.ilike(f"%{filters.title}%"))
        if filters.genres:
            query = query.join(Movie.genres).filter(Genre.name.in_(filters.genres))
        if filters.min_duration:
            query = query.filter(Movie.lengthmin >= filters.min_duration)
        if filters.max_duration:
            query = query.filter(Movie.lengthmin <= filters.max_duration)
        if filters.languages:
            query = query.filter(Movie.language.in_(filters.languages))
        if filters.age_rating:
            query = query.filter(Movie.rating == filters.age_rating)

        sort_map = {
            'title': Movie.title,
            'release_date': Movie.releasedate,
            'duration': Movie.lengthmin,
            'rating': Movie.rating
        }
        sort_col = sort_map.get(filters.sort_by, Movie.title)
        if filters.order == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        query = query.offset(filters.skip).limit(filters.limit)
        return query.all()

    def update_movie(self, eidr: str, movie_update: MovieUpdate) -> Optional[Movie]:
        movie = self.get_movie_by_eidr(eidr)
        if not movie:
            return None

        update_data = movie_update.model_dump(exclude_unset=True, exclude={'genre_ids', 'cast'})
        for field, value in update_data.items():
            if hasattr(movie, field):
                setattr(movie, field, value)

        if movie_update.genre_ids is not None:
            genres = self.db.query(Genre).filter(Genre.id.in_(movie_update.genre_ids)).all()
            movie.genres = genres

        if movie_update.cast is not None:
            self.db.query(MovieCast).filter(MovieCast.movie_eidr == eidr).delete()
            for cast_member in movie_update.cast:
                mc = MovieCast(movie_eidr=eidr, cast_member=cast_member)
                self.db.add(mc)

        self.db.commit()
        self.db.refresh(movie)
        return movie

    def delete_movie(self, eidr: str) -> bool:
        movie = self.get_movie_by_eidr(eidr)
        if not movie:
            return False
        movie.is_active = 0
        self.db.commit()
        return True

    # ==================== Discovery ====================
    def get_now_showing(self, limit: int = 20) -> List[Movie]:
        today = date.today()
        return (
            self.db.query(Movie)
            .filter(Movie.is_active == 1, Movie.releasedate <= today)
            .order_by(Movie.releasedate.desc())
            .limit(limit)
            .all()
        )

    def get_this_week(self, limit: int = 20) -> List[Movie]:
        """Movies releasing from Monday to Sunday of the current week"""
        today = date.today()
        # Monday of this week
        week_start = today - timedelta(days=today.weekday())
        # Sunday of this week
        week_end = week_start + timedelta(days=6)

        return (
            self.db.query(Movie)
            .filter(
                Movie.is_active == 1,
                Movie.releasedate >= week_start,
                Movie.releasedate <= week_end
            )
            .order_by(Movie.releasedate.asc())
            .limit(limit)
            .all()
        )

    def get_coming_soon(self, limit: int = 20) -> List[Movie]:
        """Movies releasing AFTER this week"""
        today = date.today()
        # Monday of this week
        week_start = today - timedelta(days=today.weekday())
        # Sunday of this week
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)

        return (
            self.db.query(Movie)
            .filter(Movie.is_active == 1, Movie.releasedate >= next_monday)
            .order_by(Movie.releasedate.asc())
            .limit(limit)
            .all()
        )

    # ==================== Reviews ====================
    def create_review(self, review_data: ReviewCreate, user_id: int) -> Review:
        movie = self.get_movie_by_eidr(review_data.movie_eidr)
        if not movie:
            raise ValueError(f"Movie '{review_data.movie_eidr}' not found")

        existing = self.db.query(Review).filter(
            Review.movie_eidr == review_data.movie_eidr,
            Review.user_id == user_id
        ).first()
        if existing:
            raise ValueError("You have already reviewed this movie")

        review = Review(
            movie_eidr=review_data.movie_eidr,
            user_id=user_id,
            rating=review_data.rating,
            review_text=review_data.review_text
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_movie_reviews(self, movie_eidr: str, skip: int = 0, limit: int = 10) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.movie_eidr == movie_eidr)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_review(self, review_id: int, review_update: ReviewUpdate, user_id: int) -> Optional[Review]:
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()
        if not review:
            return None
        if review_update.rating is not None:
            review.rating = review_update.rating
        if review_update.review_text is not None:
            review.review_text = review_update.review_text
        review.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, review_id: int, user_id: int) -> bool:
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True