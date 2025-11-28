"""Movie service module for CineBook API.

Provides business logic for movie, genre, and review operations.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.movie import Genre, Movie, MovieCast, Review, movie_genre_association
from app.schemas.movie import GenreCreate, MovieCreate, MovieFilter, MovieUpdate, ReviewCreate, ReviewUpdate


class MovieService:
    """Service class for movie-related operations."""

    def __init__(self, db: Session):
        """Initialize the service with a database session.

        :param db: SQLAlchemy session.
        """
        self.db = db


    # ==================== Genre Operations ====================
    def create_genre(self, genre_data: GenreCreate) -> Genre:
        """Create a new genre.

        :param genre_data: Genre creation data.
        :return: Created genre.
        :raises ValueError: If genre already exists.
        """
        existing = self.db.query(Genre).filter(Genre.name == genre_data.name).first()
        if existing:
            raise ValueError(f"Genre '{genre_data.name}' already exists")
        genre = Genre(**genre_data.model_dump())
        self.db.add(genre)
        self.db.commit()
        self.db.refresh(genre)
        return genre


    def get_all_genres(self) -> List[Genre]:
        """Retrieve all genres.

        :return: List of genres.
        """
        return self.db.query(Genre).order_by(Genre.name).all()


    def get_genre_by_id(self, genre_id: int) -> Optional[Genre]:
        """Retrieve a genre by ID.

        :param genre_id: Genre identifier.
        :return: Genre or None if not found.
        """
        return self.db.query(Genre).filter(Genre.id == genre_id).first()


    # ==================== Movie CRUD ====================
    def create_movie(self, movie_data: MovieCreate) -> Movie:
        """Create a new movie.

        :param movie_data: Movie creation data.
        :return: Created movie.
        :raises ValueError: If movie already exists.
        """
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
            is_active=1,
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
        """Retrieve a movie by EIDR.

        :param eidr: Movie EIDR identifier.
        :return: Movie or None if not found.
        """
        return self.db.query(Movie).filter(Movie.eidr == eidr).first()


    def get_movies(self, filters: MovieFilter) -> List[Movie]:
        """Retrieve movies with applied filters.

        :param filters: Movie filter criteria.
        :return: List of movies.
        """
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
            "title": Movie.title,
            "release_date": Movie.releasedate,
            "duration": Movie.lengthmin,
            "rating": Movie.rating,
        }
        sort_col = sort_map.get(filters.sort_by, Movie.title)
        if filters.order == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        query = query.offset(filters.skip).limit(filters.limit)
        return query.all()


    def update_movie(self, eidr: str, movie_update: MovieUpdate) -> Optional[Movie]:
        """Update a movie by EIDR.

        :param eidr: Movie EIDR identifier.
        :param movie_update: Update data.
        :return: Updated movie or None if not found.
        """
        movie = self.get_movie_by_eidr(eidr)
        if not movie:
            return None

        update_data = movie_update.model_dump(
            exclude_unset=True,
            exclude={"genre_ids", "cast"},
        )
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
        """Deactivate a movie by EIDR.

        :param eidr: Movie EIDR identifier.
        :return: True if deleted, False if not found.
        """
        movie = self.get_movie_by_eidr(eidr)
        if not movie:
            return False
        movie.is_active = 0
        self.db.commit()
        return True


    # ==================== Discovery ====================
    def get_now_showing(self, limit: int = 20) -> List[Movie]:
        """Retrieve currently showing movies.

        :param limit: Maximum movies to return.
        :return: List of movies.
        """
        today = date.today()
        return (
            self.db.query(Movie)
            .filter(Movie.is_active == 1, Movie.releasedate <= today)
            .order_by(Movie.releasedate.desc())
            .limit(limit)
            .all()
        )


    def get_this_week(self, limit: int = 20) -> List[Movie]:
        """Retrieve movies releasing this week (Monday to Sunday).

        :param limit: Maximum movies to return.
        :return: List of movies.
        """
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
                Movie.releasedate <= week_end,
            )
            .order_by(Movie.releasedate.asc())
            .limit(limit)
            .all()
        )


    def get_coming_soon(self, limit: int = 20) -> List[Movie]:
        """Retrieve movies releasing after this week.

        :param limit: Maximum movies to return.
        :return: List of movies.
        """
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
        """Create a new review for a movie.

        :param review_data: Review creation data.
        :param user_id: User identifier.
        :return: Created review.
        :raises ValueError: If movie not found or already reviewed.
        """
        movie = self.get_movie_by_eidr(review_data.movie_eidr)
        if not movie:
            raise ValueError(f"Movie '{review_data.movie_eidr}' not found")

        existing = self.db.query(Review).filter(
            Review.movie_eidr == review_data.movie_eidr,
            Review.user_id == user_id,
        ).first()
        if existing:
            raise ValueError("You have already reviewed this movie")

        review = Review(
            movie_eidr=review_data.movie_eidr,
            user_id=user_id,
            rating=review_data.rating,
            review_text=review_data.review_text,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review


    def get_movie_reviews(self, movie_eidr: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Retrieve reviews for a movie with pagination.

        :param movie_eidr: Movie EIDR identifier.
        :param skip: Number of records to skip.
        :param limit: Maximum records to return.
        :return: List of reviews.
        """
        return (
            self.db.query(Review)
            .filter(Review.movie_eidr == movie_eidr)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


    def update_review(self, review_id: int, review_update: ReviewUpdate, user_id: int) -> Optional[Review]:
        """Update a review by ID.

        :param review_id: Review identifier.
        :param review_update: Update data.
        :param user_id: User identifier.
        :return: Updated review or None if not found/unauthorized.
        """
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id,
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
        """Delete a review by ID.

        :param review_id: Review identifier.
        :param user_id: User identifier.
        :return: True if deleted, False if not found/unauthorized.
        """
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id,
        ).first()
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True