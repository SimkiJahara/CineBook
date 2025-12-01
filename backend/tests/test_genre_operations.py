"""Unit tests for Genre operations in CineBook API.

Tests genre creation, retrieval, and validation.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.movie import Genre
from app.schemas.movie import GenreCreate
from app.services.movie_service import MovieService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_genre.db"
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


class TestGenreCreation:
    """Test cases for genre creation."""

    def test_create_genre_success(self, movie_service):
        """Test successful genre creation."""
        genre_data = GenreCreate(name="Action", description="Action movies")
        genre = movie_service.create_genre(genre_data)
        
        assert genre.id is not None
        assert genre.name == "Action"
        assert genre.description == "Action movies"
        assert genre.created_at is not None

    def test_create_genre_without_description(self, movie_service):
        """Test creating genre without description."""
        genre_data = GenreCreate(name="Comedy")
        genre = movie_service.create_genre(genre_data)
        
        assert genre.name == "Comedy"
        assert genre.description is None

    def test_create_duplicate_genre(self, movie_service):
        """Test creating duplicate genre raises error."""
        genre_data = GenreCreate(name="Drama", description="Drama movies")
        movie_service.create_genre(genre_data)
        
        with pytest.raises(ValueError, match="already exists"):
            movie_service.create_genre(genre_data)

    def test_create_multiple_genres(self, movie_service):
        """Test creating multiple genres."""
        genres = [
            GenreCreate(name="Action"),
            GenreCreate(name="Comedy"),
            GenreCreate(name="Drama"),
        ]
        
        created_genres = []
        for genre_data in genres:
            created_genres.append(movie_service.create_genre(genre_data))
        
        assert len(created_genres) == 3
        assert all(g.id is not None for g in created_genres)


class TestGenreRetrieval:
    """Test cases for genre retrieval."""

    def test_get_all_genres_empty(self, movie_service):
        """Test retrieving genres from empty database."""
        genres = movie_service.get_all_genres()
        assert genres == []

    def test_get_all_genres(self, movie_service):
        """Test retrieving all genres."""
        # Create test genres
        test_genres = ["Action", "Comedy", "Drama", "Horror", "Thriller"]
        for name in test_genres:
            movie_service.create_genre(GenreCreate(name=name))
        
        genres = movie_service.get_all_genres()
        assert len(genres) == 5
        genre_names = [g.name for g in genres]
        assert sorted(genre_names) == sorted(test_genres)

    def test_get_genre_by_id_success(self, movie_service):
        """Test retrieving genre by ID."""
        created = movie_service.create_genre(GenreCreate(name="Sci-Fi"))
        retrieved = movie_service.get_genre_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Sci-Fi"

    def test_get_genre_by_id_not_found(self, movie_service):
        """Test retrieving non-existent genre."""
        genre = movie_service.get_genre_by_id(999)
        assert genre is None

    def test_genres_ordered_by_name(self, movie_service):
        """Test that genres are returned in alphabetical order."""
        names = ["Zombie", "Action", "Mystery", "Drama"]
        for name in names:
            movie_service.create_genre(GenreCreate(name=name))
        
        genres = movie_service.get_all_genres()
        genre_names = [g.name for g in genres]
        assert genre_names == sorted(names)


class TestGenreValidation:
    """Test cases for genre validation."""

    def test_genre_name_required(self):
        """Test that genre name is required."""
        with pytest.raises(Exception):
            GenreCreate()

    def test_genre_name_max_length(self):
     long_name = "A" * 51  # Exceeds 50 char limit
    # Pydantic should reject this - expect ValidationError
     with pytest.raises(Exception):
        genre_data = GenreCreate(name=long_name)

    def test_genre_description_optional(self):
        """Test that description is optional."""
        genre_data = GenreCreate(name="Western")
        assert genre_data.description is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])