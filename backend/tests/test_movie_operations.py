"""Unit tests for Movie CRUD operations in CineBook API.

Tests movie creation, retrieval, update, and deletion.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.movie import Movie, Genre, MovieCast
from app.schemas.movie import MovieCreate, MovieUpdate, GenreCreate
from app.services.movie_service import MovieService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_movies.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def movie_service(db_session):
    """Create MovieService instance with test database."""
    return MovieService(db_session)


@pytest.fixture
def sample_genres(movie_service):
    """Create sample genres for testing."""
    genres = []
    for name in ["Action", "Comedy", "Drama"]:
        genre = movie_service.create_genre(GenreCreate(name=name))
        genres.append(genre)
    return genres


class TestMovieCreation:
    """Test cases for movie creation."""

    def test_create_movie_success(self, movie_service, sample_genres):
        """Test successful movie creation with all fields."""
        movie_data = MovieCreate(
            eidr="10.5240/AAAA-BBBB-CCCC-DDDD",
            title="Inception",
            posterurl="https://example.com/poster.jpg",
            lengthmin=148,
            rating="PG-13",
            releasedate=date(2010, 7, 16),
            description="A mind-bending thriller",
            director="Christopher Nolan",
            trailerurl="https://example.com/trailer.mp4",
            language="English",
            genre_ids=[sample_genres[0].id],
            cast=["Leonardo DiCaprio", "Tom Hardy"]
        )
        
        movie = movie_service.create_movie(movie_data)
        
        assert movie.eidr == "10.5240/AAAA-BBBB-CCCC-DDDD"
        assert movie.title == "Inception"
        assert movie.lengthmin == 148
        assert movie.rating == "PG-13"
        assert movie.director == "Christopher Nolan"
        assert movie.is_active == 1
        assert len(movie.genres) == 1
        assert len(movie.cast) == 2

    def test_create_movie_minimal_fields(self, movie_service):
        """Test creating movie with only required fields."""
        movie_data = MovieCreate(
            eidr="10.5240/XXXX-YYYY-ZZZZ",
            title="Minimal Movie"
        )
        
        movie = movie_service.create_movie(movie_data)
        
        assert movie.eidr == "10.5240/XXXX-YYYY-ZZZZ"
        assert movie.title == "Minimal Movie"
        assert movie.language == "English"  # Default value
        assert movie.is_active == 1

    def test_create_duplicate_movie(self, movie_service):
        """Test creating duplicate movie raises error."""
        movie_data = MovieCreate(
            eidr="10.5240/DUPLICATE",
            title="Test Movie"
        )
        
        movie_service.create_movie(movie_data)
        
        with pytest.raises(ValueError, match="already exists"):
            movie_service.create_movie(movie_data)

    def test_create_movie_with_multiple_genres(self, movie_service, sample_genres):
        """Test creating movie with multiple genres."""
        movie_data = MovieCreate(
            eidr="10.5240/MULTI-GENRE",
            title="Action Comedy",
            genre_ids=[sample_genres[0].id, sample_genres[1].id]
        )
        
        movie = movie_service.create_movie(movie_data)
        
        assert len(movie.genres) == 2
        genre_names = [g.name for g in movie.genres]
        assert "Action" in genre_names
        assert "Comedy" in genre_names

    def test_create_movie_with_cast(self, movie_service):
        """Test creating movie with cast members."""
        movie_data = MovieCreate(
            eidr="10.5240/WITH-CAST",
            title="Star-Studded Film",
            cast=["Actor One", "Actor Two", "Actor Three"]
        )
        
        movie = movie_service.create_movie(movie_data)
        
        assert len(movie.cast) == 3
        assert "Actor One" in movie.cast


class TestMovieRetrieval:
    """Test cases for movie retrieval."""

    def test_get_movie_by_eidr_success(self, movie_service):
        """Test retrieving movie by EIDR."""
        movie_data = MovieCreate(
            eidr="10.5240/GET-TEST",
            title="Test Movie"
        )
        created = movie_service.create_movie(movie_data)
        
        retrieved = movie_service.get_movie_by_eidr("10.5240/GET-TEST")
        
        assert retrieved is not None
        assert retrieved.eidr == created.eidr
        assert retrieved.title == "Test Movie"

    def test_get_movie_by_eidr_not_found(self, movie_service):
        """Test retrieving non-existent movie."""
        movie = movie_service.get_movie_by_eidr("10.5240/NOT-EXIST")
        assert movie is None

    def test_get_movies_empty_database(self, movie_service):
        """Test retrieving movies from empty database."""
        from app.schemas.movie import MovieFilter
        filters = MovieFilter()
        movies = movie_service.get_movies(filters)
        assert movies == []

    def test_get_movies_with_title_filter(self, movie_service):
        """Test filtering movies by title."""
        from app.schemas.movie import MovieFilter
        
        # Create test movies
        movie_service.create_movie(MovieCreate(eidr="1", title="The Matrix"))
        movie_service.create_movie(MovieCreate(eidr="2", title="The Matrix Reloaded"))
        movie_service.create_movie(MovieCreate(eidr="3", title="Inception"))
        
        filters = MovieFilter(title="Matrix")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        titles = [m.title for m in movies]
        assert all("Matrix" in t for t in titles)

    def test_get_movies_with_duration_filter(self, movie_service):
        """Test filtering movies by duration."""
        from app.schemas.movie import MovieFilter
        
        movie_service.create_movie(MovieCreate(eidr="1", title="Short", lengthmin=90))
        movie_service.create_movie(MovieCreate(eidr="2", title="Medium", lengthmin=120))
        movie_service.create_movie(MovieCreate(eidr="3", title="Long", lengthmin=180))
        
        filters = MovieFilter(min_duration=100, max_duration=150)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].title == "Medium"

    def test_get_movies_pagination(self, movie_service):
        """Test movie pagination."""
        from app.schemas.movie import MovieFilter
        
        # Create 5 test movies
        for i in range(5):
            movie_service.create_movie(MovieCreate(eidr=f"EIDR-{i}", title=f"Movie {i}"))
        
        filters = MovieFilter(skip=2, limit=2)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2


class TestMovieUpdate:
    """Test cases for movie updates."""

    def test_update_movie_success(self, movie_service):
        """Test successful movie update."""
        movie_data = MovieCreate(eidr="10.5240/UPDATE", title="Original Title")
        movie_service.create_movie(movie_data)
        
        update_data = MovieUpdate(title="Updated Title", director="New Director")
        updated = movie_service.update_movie("10.5240/UPDATE", update_data)
        
        assert updated.title == "Updated Title"
        assert updated.director == "New Director"

    def test_update_movie_not_found(self, movie_service):
        """Test updating non-existent movie."""
        update_data = MovieUpdate(title="New Title")
        result = movie_service.update_movie("10.5240/NOT-EXIST", update_data)
        
        assert result is None

    def test_update_movie_partial_fields(self, movie_service):
        """Test updating only specific fields."""
        movie_data = MovieCreate(
            eidr="10.5240/PARTIAL",
            title="Original",
            director="Original Director",
            lengthmin=120
        )
        movie_service.create_movie(movie_data)
        
        update_data = MovieUpdate(director="New Director")
        updated = movie_service.update_movie("10.5240/PARTIAL", update_data)
        
        assert updated.title == "Original"  # Unchanged
        assert updated.director == "New Director"  # Changed
        assert updated.lengthmin == 120  # Unchanged

    def test_update_movie_genres(self, movie_service, sample_genres):
        """Test updating movie genres."""
        movie_data = MovieCreate(
            eidr="10.5240/GENRE-UPDATE",
            title="Test",
            genre_ids=[sample_genres[0].id]
        )
        movie_service.create_movie(movie_data)
        
        update_data = MovieUpdate(genre_ids=[sample_genres[1].id, sample_genres[2].id])
        updated = movie_service.update_movie("10.5240/GENRE-UPDATE", update_data)
        
        assert len(updated.genres) == 2
        genre_names = [g.name for g in updated.genres]
        assert "Comedy" in genre_names
        assert "Drama" in genre_names

    def test_update_movie_cast(self, movie_service):
        """Test updating movie cast."""
        movie_data = MovieCreate(
            eidr="10.5240/CAST-UPDATE",
            title="Test",
            cast=["Actor A", "Actor B"]
        )
        movie_service.create_movie(movie_data)
        
        update_data = MovieUpdate(cast=["Actor C", "Actor D", "Actor E"])
        updated = movie_service.update_movie("10.5240/CAST-UPDATE", update_data)
        
        assert len(updated.cast) == 3
        assert "Actor C" in updated.cast


class TestMovieDeletion:
    """Test cases for movie deletion (soft delete)."""

    def test_delete_movie_success(self, movie_service):
        """Test successful movie deletion."""
        movie_data = MovieCreate(eidr="10.5240/DELETE", title="To Delete")
        movie_service.create_movie(movie_data)
        
        result = movie_service.delete_movie("10.5240/DELETE")
        
        assert result is True
        deleted = movie_service.get_movie_by_eidr("10.5240/DELETE")
        assert deleted.is_active == 0

    def test_delete_movie_not_found(self, movie_service):
        """Test deleting non-existent movie."""
        result = movie_service.delete_movie("10.5240/NOT-EXIST")
        assert result is False

    def test_deleted_movie_not_in_listings(self, movie_service):
        """Test that deleted movies don't appear in listings."""
        from app.schemas.movie import MovieFilter
        
        movie_service.create_movie(MovieCreate(eidr="1", title="Active"))
        movie_service.create_movie(MovieCreate(eidr="2", title="To Delete"))
        
        movie_service.delete_movie("2")
        
        filters = MovieFilter()
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].title == "Active"


class TestMovieProperties:
    """Test cases for movie computed properties."""

    def test_movie_average_rating_no_reviews(self, movie_service):
        """Test average rating with no reviews."""
        movie_data = MovieCreate(eidr="10.5240/NO-REVIEWS", title="Test")
        movie = movie_service.create_movie(movie_data)
        
        assert movie.average_rating == 0.0

    def test_movie_review_count_zero(self, movie_service):
        """Test review count with no reviews."""
        movie_data = MovieCreate(eidr="10.5240/COUNT", title="Test")
        movie = movie_service.create_movie(movie_data)
        
        assert movie.review_count == 0

    def test_movie_cast_property(self, movie_service):
        """Test cast property returns list of strings."""
        movie_data = MovieCreate(
            eidr="10.5240/CAST-PROP",
            title="Test",
            cast=["Actor One", "Actor Two"]
        )
        movie = movie_service.create_movie(movie_data)
        
        assert isinstance(movie.cast, list)
        assert len(movie.cast) == 2
        assert "Actor One" in movie.cast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])