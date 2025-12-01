"""Unit tests for Movie Discovery features in CineBook API.

Tests now showing, this week, and coming soon movie discovery endpoints.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.schemas.movie import MovieCreate
from app.services.movie_service import MovieService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_discovery.db"
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
def create_movie_helper(movie_service):
    """Helper function to create movies with specific release dates."""
    def _create_movie(eidr_suffix, title, release_date):
        movie_data = MovieCreate(
            eidr=f"10.5240/{eidr_suffix}",
            title=title,
            releasedate=release_date
        )
        return movie_service.create_movie(movie_data)
    return _create_movie


class TestNowShowingMovies:
    """Test cases for now showing movie discovery."""

    def test_now_showing_empty(self, movie_service):
        """Test now showing with no movies."""
        movies = movie_service.get_now_showing()
        assert movies == []

    def test_now_showing_returns_past_movies(self, movie_service, create_movie_helper):
        """Test that now showing returns movies released in the past."""
        today = date.today()
        
        # Create movies released in the past
        create_movie_helper("PAST1", "Last Week", today - timedelta(days=7))
        create_movie_helper("PAST2", "Last Month", today - timedelta(days=30))
        create_movie_helper("PAST3", "Yesterday", today - timedelta(days=1))
        
        movies = movie_service.get_now_showing()
        
        assert len(movies) == 3
        titles = [m.title for m in movies]
        assert "Last Week" in titles
        assert "Last Month" in titles
        assert "Yesterday" in titles

    def test_now_showing_includes_today(self, movie_service, create_movie_helper):
        """Test that now showing includes movies released today."""
        today = date.today()
        create_movie_helper("TODAY", "Released Today", today)
        
        movies = movie_service.get_now_showing()
        
        assert len(movies) == 1
        assert movies[0].title == "Released Today"

    def test_now_showing_excludes_future(self, movie_service, create_movie_helper):
        """Test that now showing excludes future movies."""
        today = date.today()
        
        create_movie_helper("PAST", "Released Yesterday", today - timedelta(days=1))
        create_movie_helper("FUTURE", "Coming Tomorrow", today + timedelta(days=1))
        
        movies = movie_service.get_now_showing()
        
        assert len(movies) == 1
        assert movies[0].title == "Released Yesterday"

    def test_now_showing_ordered_by_release_date_desc(self, movie_service, create_movie_helper):
        """Test that now showing movies are ordered by release date (newest first)."""
        today = date.today()
        
        create_movie_helper("OLD", "Old Movie", today - timedelta(days=30))
        create_movie_helper("RECENT", "Recent Movie", today - timedelta(days=7))
        create_movie_helper("TODAY", "Today's Movie", today)
        
        movies = movie_service.get_now_showing()
        
        assert movies[0].title == "Today's Movie"
        assert movies[1].title == "Recent Movie"
        assert movies[2].title == "Old Movie"

    def test_now_showing_respects_limit(self, movie_service, create_movie_helper):
        """Test that now showing respects the limit parameter."""
        today = date.today()
        
        # Create 5 movies
        for i in range(5):
            create_movie_helper(f"MOVIE{i}", f"Movie {i}", today - timedelta(days=i))
        
        movies = movie_service.get_now_showing(limit=3)
        
        assert len(movies) == 3

    def test_now_showing_excludes_inactive(self, movie_service, create_movie_helper):
        """Test that now showing excludes inactive movies."""
        today = date.today()
        
        movie = create_movie_helper("ACTIVE", "Active Movie", today - timedelta(days=1))
        inactive_movie = create_movie_helper("INACTIVE", "Inactive Movie", today - timedelta(days=2))
        
        # Deactivate one movie
        movie_service.delete_movie(inactive_movie.eidr)
        
        movies = movie_service.get_now_showing()
        
        assert len(movies) == 1
        assert movies[0].title == "Active Movie"


class TestThisWeekMovies:
    """Test cases for this week movie discovery."""

    def test_this_week_empty(self, movie_service):
        """Test this week with no movies."""
        movies = movie_service.get_this_week()
        assert movies == []

    def test_this_week_current_week_movies(self, movie_service, create_movie_helper):
        """Test that this week returns movies from current week."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        
        # Create movies within this week
        create_movie_helper("MON", "Monday Release", week_start)
        create_movie_helper("WED", "Wednesday Release", week_start + timedelta(days=2))
        create_movie_helper("FRI", "Friday Release", week_start + timedelta(days=4))
        
        movies = movie_service.get_this_week()
        
        assert len(movies) == 3

    def test_this_week_excludes_last_week(self, movie_service, create_movie_helper):
        """Test that this week excludes last week's movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        last_week = week_start - timedelta(days=7)
        
        create_movie_helper("THIS", "This Week", week_start)
        create_movie_helper("LAST", "Last Week", last_week)
        
        movies = movie_service.get_this_week()
        
        assert len(movies) == 1
        assert movies[0].title == "This Week"

    def test_this_week_excludes_next_week(self, movie_service, create_movie_helper):
        """Test that this week excludes next week's movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        next_week = week_start + timedelta(days=7)
        
        create_movie_helper("THIS", "This Week", week_start)
        create_movie_helper("NEXT", "Next Week", next_week)
        
        movies = movie_service.get_this_week()
        
        assert len(movies) == 1
        assert movies[0].title == "This Week"

    def test_this_week_includes_sunday(self, movie_service, create_movie_helper):
        """Test that this week includes Sunday (end of week)."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)  # Sunday
        
        create_movie_helper("SUN", "Sunday Release", week_end)
        
        movies = movie_service.get_this_week()
        
        assert len(movies) == 1
        assert movies[0].title == "Sunday Release"

    def test_this_week_ordered_by_release_date_asc(self, movie_service, create_movie_helper):
        """Test that this week movies are ordered by release date (earliest first)."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        create_movie_helper("FRI", "Friday", week_start + timedelta(days=4))
        create_movie_helper("MON", "Monday", week_start)
        create_movie_helper("WED", "Wednesday", week_start + timedelta(days=2))
        
        movies = movie_service.get_this_week()
        
        assert movies[0].title == "Monday"
        assert movies[1].title == "Wednesday"
        assert movies[2].title == "Friday"

    def test_this_week_respects_limit(self, movie_service, create_movie_helper):
        """Test that this week respects the limit parameter."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Create 5 movies this week
        for i in range(5):
            create_movie_helper(f"DAY{i}", f"Day {i}", week_start + timedelta(days=i))
        
        movies = movie_service.get_this_week(limit=3)
        
        assert len(movies) == 3

    def test_this_week_excludes_inactive(self, movie_service, create_movie_helper):
        """Test that this week excludes inactive movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        active = create_movie_helper("ACTIVE", "Active", week_start)
        inactive = create_movie_helper("INACTIVE", "Inactive", week_start + timedelta(days=1))
        
        movie_service.delete_movie(inactive.eidr)
        
        movies = movie_service.get_this_week()
        
        assert len(movies) == 1
        assert movies[0].title == "Active"


class TestComingSoonMovies:
    """Test cases for coming soon movie discovery."""

    def test_coming_soon_empty(self, movie_service):
        """Test coming soon with no movies."""
        movies = movie_service.get_coming_soon()
        assert movies == []

    def test_coming_soon_future_movies(self, movie_service, create_movie_helper):
        """Test that coming soon returns future movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)
        
        create_movie_helper("NEXT1", "Next Week", next_monday)
        create_movie_helper("NEXT2", "Two Weeks", next_monday + timedelta(days=7))
        create_movie_helper("NEXT3", "Next Month", next_monday + timedelta(days=30))
        
        movies = movie_service.get_coming_soon()
        
        assert len(movies) == 3

    def test_coming_soon_excludes_this_week(self, movie_service, create_movie_helper):
        """Test that coming soon excludes this week's movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)
        
        create_movie_helper("THIS", "This Week", week_start)
        create_movie_helper("NEXT", "Next Week", next_monday)
        
        movies = movie_service.get_coming_soon()
        
        assert len(movies) == 1
        assert movies[0].title == "Next Week"

    def test_coming_soon_excludes_past(self, movie_service, create_movie_helper):
        """Test that coming soon excludes past movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)
        
        create_movie_helper("PAST", "Past Movie", today - timedelta(days=30))
        create_movie_helper("FUTURE", "Future Movie", next_monday)
        
        movies = movie_service.get_coming_soon()
        
        assert len(movies) == 1
        assert movies[0].title == "Future Movie"

    def test_coming_soon_starts_after_this_week(self, movie_service, create_movie_helper):
        """Test that coming soon starts from next Monday."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)  # Sunday
        next_monday = week_end + timedelta(days=1)
        
        # Create movie on Sunday (should not appear)
        create_movie_helper("SUN", "Sunday", week_end)
        
        # Create movie on Monday (should appear)
        create_movie_helper("MON", "Monday", next_monday)
        
        movies = movie_service.get_coming_soon()
        
        assert len(movies) == 1
        assert movies[0].title == "Monday"

    def test_coming_soon_ordered_by_release_date_asc(self, movie_service, create_movie_helper):
        """Test that coming soon movies are ordered by release date (earliest first)."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)
        
        create_movie_helper("FAR", "Far Future", next_monday + timedelta(days=30))
        create_movie_helper("NEAR", "Near Future", next_monday)
        create_movie_helper("MID", "Mid Future", next_monday + timedelta(days=14))
        
        movies = movie_service.get_coming_soon()
        
        assert movies[0].title == "Near Future"
        assert movies[1].title == "Mid Future"
        assert movies[2].title == "Far Future"

    def test_coming_soon_respects_limit(self, movie_service, create_movie_helper):
        """Test that coming soon respects the limit parameter."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)
        
        # Create 5 future movies
        for i in range(5):
            create_movie_helper(f"FUTURE{i}", f"Future {i}", next_monday + timedelta(days=i))
        
        movies = movie_service.get_coming_soon(limit=3)
        
        assert len(movies) == 3

    def test_coming_soon_excludes_inactive(self, movie_service, create_movie_helper):
        """Test that coming soon excludes inactive movies."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_monday = week_end + timedelta(days=1)
        
        active = create_movie_helper("ACTIVE", "Active", next_monday)
        inactive = create_movie_helper("INACTIVE", "Inactive", next_monday + timedelta(days=1))
        
        movie_service.delete_movie(inactive.eidr)
        
        movies = movie_service.get_coming_soon()
        
        assert len(movies) == 1
        assert movies[0].title == "Active"


class TestDiscoveryEdgeCases:
    """Test edge cases for discovery features."""

    def test_movies_without_release_dates(self, movie_service):
        """Test handling of movies without release dates."""
        from app.schemas.movie import MovieCreate
        
        # Create movie without release date
        movie_data = MovieCreate(
            eidr="10.5240/NO-DATE",
            title="No Release Date"
        )
        movie_service.create_movie(movie_data)
        
        # Should not appear in any discovery endpoint
        assert len(movie_service.get_now_showing()) == 0
        assert len(movie_service.get_this_week()) == 0
        assert len(movie_service.get_coming_soon()) == 0

    def test_all_discovery_endpoints_together(self, movie_service, create_movie_helper):
  
     today = date.today()
     week_start = today - timedelta(days=today.weekday())
     week_end = week_start + timedelta(days=6)
     next_monday = week_end + timedelta(days=1)
    
    # Past movies (guaranteed to be in the past)
     create_movie_helper("PAST1", "Last Month", today - timedelta(days=30))
     create_movie_helper("PAST2", "Last Week", week_start - timedelta(days=7))
    
    # This week - only create if not in the future
     create_movie_helper("THIS1", "Monday", week_start)
     friday = week_start + timedelta(days=4)
     if friday <= today:
         create_movie_helper("THIS2", "Friday", friday)
         expected_now_showing = 4
         expected_this_week = 2
     else:
         expected_now_showing = 3
         expected_this_week = 1
    
    # Coming soon
     create_movie_helper("NEXT1", "Next Week", next_monday)
     create_movie_helper("NEXT2", "Far Future", next_monday + timedelta(days=30))
    
    # Now showing should have: past movies + this week (only past/today)
     now_showing = movie_service.get_now_showing()
     assert len(now_showing) == expected_now_showing
    
    # This week should have only this week's movies
     this_week = movie_service.get_this_week()
     assert len(this_week) == expected_this_week
    
    # Coming soon should have only future movies
     coming_soon = movie_service.get_coming_soon()
     assert len(coming_soon) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])