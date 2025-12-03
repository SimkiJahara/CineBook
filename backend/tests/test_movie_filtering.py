"""Unit tests for Movie Filtering features in CineBook API.

Tests filtering by title, genre, duration, language, and rating.
"""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.schemas.movie import MovieCreate, MovieFilter, GenreCreate
from app.services.movie_service import MovieService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_filtering.db"
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
    genres = {}
    for name in ["Action", "Comedy", "Drama", "Horror", "Sci-Fi"]:
        genre = movie_service.create_genre(GenreCreate(name=name))
        genres[name] = genre
    return genres


@pytest.fixture
def sample_movies(movie_service, sample_genres):
    """Create a diverse set of sample movies for filtering tests."""
    movies_data = [
        {
            "eidr": "10.5240/MOVIE-001",
            "title": "The Action Hero",
            "lengthmin": 120,
            "rating": "PG-13",
            "language": "English",
            "genre_ids": [sample_genres["Action"].id]
        },
        {
            "eidr": "10.5240/MOVIE-002",
            "title": "Comedy Central",
            "lengthmin": 95,
            "rating": "PG",
            "language": "English",
            "genre_ids": [sample_genres["Comedy"].id]
        },
        {
            "eidr": "10.5240/MOVIE-003",
            "title": "The Drama Queen",
            "lengthmin": 150,
            "rating": "R",
            "language": "English",
            "genre_ids": [sample_genres["Drama"].id]
        },
        {
            "eidr": "10.5240/MOVIE-004",
            "title": "Space Adventure",
            "lengthmin": 140,
            "rating": "PG-13",
            "language": "English",
            "genre_ids": [sample_genres["Sci-Fi"].id, sample_genres["Action"].id]
        },
        {
            "eidr": "10.5240/MOVIE-005",
            "title": "Horror Night",
            "lengthmin": 88,
            "rating": "R",
            "language": "English",
            "genre_ids": [sample_genres["Horror"].id]
        },
        {
            "eidr": "10.5240/MOVIE-006",
            "title": "French Romance",
            "lengthmin": 110,
            "rating": "PG-13",
            "language": "French",
            "genre_ids": [sample_genres["Drama"].id]
        },
        {
            "eidr": "10.5240/MOVIE-007",
            "title": "Spanish Comedy",
            "lengthmin": 100,
            "rating": "PG",
            "language": "Spanish",
            "genre_ids": [sample_genres["Comedy"].id]
        },
    ]
    
    for data in movies_data:
        movie_service.create_movie(MovieCreate(**data))


class TestTitleFiltering:
    """Test cases for filtering by title."""

    def test_filter_by_exact_title(self, movie_service, sample_movies):
        """Test filtering by exact title match."""
        filters = MovieFilter(title="Comedy Central")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].title == "Comedy Central"

    def test_filter_by_partial_title(self, movie_service, sample_movies):
        """Test filtering by partial title (case-insensitive)."""
        filters = MovieFilter(title="comedy")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        titles = [m.title for m in movies]
        assert "Comedy Central" in titles
        assert "Spanish Comedy" in titles

    def test_filter_title_case_insensitive(self, movie_service, sample_movies):
   
    # Search for "ACTION" in uppercase - should match "The Action Hero"
     filters = MovieFilter(title="ACTION")
     movies = movie_service.get_movies(filters)
    
    # Should find "The Action Hero" (which contains "Action")
     assert len(movies) == 1
     assert movies[0].title == "The Action Hero"
    
    # Now test with "adventure" to verify it finds "Space Adventure"cd
     filters2 = MovieFilter(title="ADVENTURE")
     movies2 = movie_service.get_movies(filters2)
    
     assert len(movies2) == 1
     assert movies2[0].title == "Space Adventure"

    def test_filter_title_substring(self, movie_service, sample_movies):
        """Test filtering with substring matching."""
        filters = MovieFilter(title="The")
        movies = movie_service.get_movies(filters)
        
        # Should match "The Action Hero" and "The Drama Queen"
        assert len(movies) == 2

    def test_filter_title_no_results(self, movie_service, sample_movies):
        """Test filtering with title that matches nothing."""
        filters = MovieFilter(title="NonExistent")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 0


class TestGenreFiltering:
    """Test cases for filtering by genre."""

    def test_filter_by_single_genre(self, movie_service, sample_movies):
        """Test filtering by a single genre."""
        filters = MovieFilter(genres=["Action"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        titles = [m.title for m in movies]
        assert "The Action Hero" in titles
        assert "Space Adventure" in titles

    def test_filter_by_multiple_genres(self, movie_service, sample_movies):
        """Test filtering by multiple genres (OR logic)."""
        filters = MovieFilter(genres=["Comedy", "Horror"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 3
        titles = [m.title for m in movies]
        assert "Comedy Central" in titles
        assert "Spanish Comedy" in titles
        assert "Horror Night" in titles

    def test_filter_genre_no_results(self, movie_service, sample_movies, sample_genres):
        """Test filtering by genre with no matches."""
        # Create a genre but no movies with it
        new_genre = movie_service.create_genre(GenreCreate(name="Western"))
        
        filters = MovieFilter(genres=["Western"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 0

    def test_filter_multi_genre_movie(self, movie_service, sample_movies):
        """Test that multi-genre movies appear in correct filters."""
        # Space Adventure has both Sci-Fi and Action
        filters = MovieFilter(genres=["Sci-Fi"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].title == "Space Adventure"


class TestDurationFiltering:
    """Test cases for filtering by duration."""

    def test_filter_by_min_duration(self, movie_service, sample_movies):
        """Test filtering by minimum duration."""
        filters = MovieFilter(min_duration=120)
        movies = movie_service.get_movies(filters)
        
        # Should include movies >= 120 minutes
        durations = [m.lengthmin for m in movies]
        assert all(d >= 120 for d in durations)
        assert len(movies) == 3  # 120, 140, 150

    def test_filter_by_max_duration(self, movie_service, sample_movies):
        """Test filtering by maximum duration."""
        filters = MovieFilter(max_duration=100)
        movies = movie_service.get_movies(filters)
        
        # Should include movies <= 100 minutes
        durations = [m.lengthmin for m in movies]
        assert all(d <= 100 for d in durations)
        assert len(movies) == 3  # 88, 95, 100

    def test_filter_by_duration_range(self, movie_service, sample_movies):
        """Test filtering by duration range."""
        filters = MovieFilter(min_duration=90, max_duration=120)
        movies = movie_service.get_movies(filters)
        
        # Should include movies between 90 and 120 minutes
        durations = [m.lengthmin for m in movies]
        assert all(90 <= d <= 120 for d in durations)
        assert len(movies) == 4  # 95, 100, 110, 120

    def test_filter_exact_duration(self, movie_service, sample_movies):
        """Test filtering by exact duration."""
        filters = MovieFilter(min_duration=120, max_duration=120)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].lengthmin == 120

    def test_filter_duration_no_results(self, movie_service, sample_movies):
        """Test duration filter with no matches."""
        filters = MovieFilter(min_duration=200)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 0


class TestLanguageFiltering:
    """Test cases for filtering by language."""

    def test_filter_by_single_language(self, movie_service, sample_movies):
        """Test filtering by single language."""
        filters = MovieFilter(languages=["English"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 5
        languages = [m.language for m in movies]
        assert all(lang == "English" for lang in languages)

    def test_filter_by_multiple_languages(self, movie_service, sample_movies):
        """Test filtering by multiple languages."""
        filters = MovieFilter(languages=["French", "Spanish"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        titles = [m.title for m in movies]
        assert "French Romance" in titles
        assert "Spanish Comedy" in titles

    def test_filter_language_no_results(self, movie_service, sample_movies):
        """Test language filter with no matches."""
        filters = MovieFilter(languages=["German"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 0


class TestRatingFiltering:
    """Test cases for filtering by age rating."""

    def test_filter_by_pg_rating(self, movie_service, sample_movies):
        """Test filtering by PG rating."""
        filters = MovieFilter(age_rating="PG")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        ratings = [m.rating for m in movies]
        assert all(r == "PG" for r in ratings)

    def test_filter_by_pg13_rating(self, movie_service, sample_movies):
        """Test filtering by PG-13 rating."""
        filters = MovieFilter(age_rating="PG-13")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 3

    def test_filter_by_r_rating(self, movie_service, sample_movies):
        """Test filtering by R rating."""
        filters = MovieFilter(age_rating="R")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        titles = [m.title for m in movies]
        assert "The Drama Queen" in titles
        assert "Horror Night" in titles

    def test_filter_rating_no_results(self, movie_service, sample_movies):
        """Test rating filter with no matches."""
        filters = MovieFilter(age_rating="G")
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 0


class TestCombinedFiltering:
    """Test cases for combining multiple filters."""

    def test_filter_title_and_genre(self, movie_service, sample_movies):
        """Test combining title and genre filters."""
        filters = MovieFilter(title="Comedy", genres=["Comedy"])
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 2
        assert all("Comedy" in m.title for m in movies)

    def test_filter_genre_and_duration(self, movie_service, sample_movies):
        """Test combining genre and duration filters."""
        filters = MovieFilter(genres=["Action"], min_duration=130)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].title == "Space Adventure"

    def test_filter_all_criteria(self, movie_service, sample_movies):
        """Test combining all filter criteria."""
        filters = MovieFilter(
            genres=["Comedy"],
            min_duration=90,
            max_duration=100,
            languages=["Spanish"],
            age_rating="PG"
        )
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1
        assert movies[0].title == "Spanish Comedy"

    def test_filter_conflicting_criteria(self, movie_service, sample_movies):
    
     filters = MovieFilter(
        genres=["Horror"],  # Horror genre
        age_rating="G"  # But no Horror movies have G rating
     )
     movies = movie_service.get_movies(filters)
    
     assert len(movies) == 0


class TestSortingAndOrdering:
    """Test cases for sorting and ordering results."""

    def test_sort_by_title_ascending(self, movie_service, sample_movies):
        """Test sorting by title in ascending order."""
        filters = MovieFilter(sort_by="title", order="asc")
        movies = movie_service.get_movies(filters)
        
        titles = [m.title for m in movies]
        assert titles == sorted(titles)

    def test_sort_by_title_descending(self, movie_service, sample_movies):
        """Test sorting by title in descending order."""
        filters = MovieFilter(sort_by="title", order="desc")
        movies = movie_service.get_movies(filters)
        
        titles = [m.title for m in movies]
        assert titles == sorted(titles, reverse=True)

    def test_sort_by_duration_ascending(self, movie_service, sample_movies):
        """Test sorting by duration in ascending order."""
        filters = MovieFilter(sort_by="duration", order="asc")
        movies = movie_service.get_movies(filters)
        
        durations = [m.lengthmin for m in movies]
        assert durations == sorted(durations)

    def test_sort_by_duration_descending(self, movie_service, sample_movies):
        """Test sorting by duration in descending order."""
        filters = MovieFilter(sort_by="duration", order="desc")
        movies = movie_service.get_movies(filters)
        
        durations = [m.lengthmin for m in movies]
        assert durations == sorted(durations, reverse=True)

    def test_default_sorting(self, movie_service, sample_movies):
        """Test default sorting (by title ascending)."""
        filters = MovieFilter()
        movies = movie_service.get_movies(filters)
        
        titles = [m.title for m in movies]
        assert titles == sorted(titles)


class TestPagination:
    """Test cases for pagination."""

    def test_pagination_first_page(self, movie_service, sample_movies):
        """Test getting first page of results."""
        filters = MovieFilter(skip=0, limit=3)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 3

    def test_pagination_second_page(self, movie_service, sample_movies):
        """Test getting second page of results."""
        filters = MovieFilter(skip=3, limit=3)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 3

    def test_pagination_last_page_partial(self, movie_service, sample_movies):
        """Test getting last page with fewer items than limit."""
        filters = MovieFilter(skip=6, limit=3)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1

    def test_pagination_beyond_results(self, movie_service, sample_movies):
        """Test pagination beyond available results."""
        filters = MovieFilter(skip=100, limit=10)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 0

    def test_pagination_limit_zero(self, movie_service, sample_movies):
        """Test pagination with limit of 1."""
        filters = MovieFilter(skip=0, limit=1)
        movies = movie_service.get_movies(filters)
        
        assert len(movies) == 1


class TestActiveStatusFiltering:
    """Test cases for filtering active movies only."""

    def test_only_active_movies_returned(self, movie_service, sample_movies):
        """Test that only active movies are returned by default."""
        # Deactivate one movie
        movie_service.delete_movie("10.5240/MOVIE-001")
        
        filters = MovieFilter()
        movies = movie_service.get_movies(filters)
        
        # Should return 6 out of 7 movies
        assert len(movies) == 6
        assert all(m.is_active == 1 for m in movies)

    def test_inactive_movie_not_in_any_filter(self, movie_service, sample_movies):
        """Test that inactive movies don't appear in any filter results."""
        movie_service.delete_movie("10.5240/MOVIE-002")
        
        # Try various filters
        filters = [
            MovieFilter(title="Comedy"),
            MovieFilter(genres=["Comedy"]),
            MovieFilter(min_duration=90, max_duration=100),
        ]
        
        for f in filters:
            movies = movie_service.get_movies(f)
            titles = [m.title for m in movies]
            assert "Comedy Central" not in titles


if __name__ == "__main__":
    pytest.main([__file__, "-v"])