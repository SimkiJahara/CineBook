"""Unit tests for Review operations in CineBook API.

Tests review creation, retrieval, update, and deletion.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.movie import Review
from app.schemas.movie import ReviewCreate, ReviewUpdate, MovieCreate
from app.services.movie_service import MovieService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_reviews.db"
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
def sample_movie(movie_service):
    """Create a sample movie for testing reviews."""
    movie_data = MovieCreate(
        eidr="10.5240/TEST-MOVIE",
        title="Test Movie"
    )
    return movie_service.create_movie(movie_data)


class TestReviewCreation:
    """Test cases for review creation."""

    def test_create_review_success(self, movie_service, sample_movie):
        """Test successful review creation."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.5,
            review_text="Great movie!"
        )
        
        review = movie_service.create_review(review_data, user_id=1)
        
        assert review.id is not None
        assert review.movie_eidr == sample_movie.eidr
        assert review.user_id == 1
        assert review.rating == 4.5
        assert review.review_text == "Great movie!"
        assert review.created_at is not None

    def test_create_review_without_text(self, movie_service, sample_movie):
        """Test creating review without review text."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=3.0
        )
        
        review = movie_service.create_review(review_data, user_id=1)
        
        assert review.rating == 3.0
        assert review.review_text is None

    def test_create_review_movie_not_found(self, movie_service):
        """Test creating review for non-existent movie."""
        review_data = ReviewCreate(
            movie_eidr="10.5240/NOT-EXIST",
            rating=4.0
        )
        
        with pytest.raises(ValueError, match="not found"):
            movie_service.create_review(review_data, user_id=1)

    def test_create_duplicate_review(self, movie_service, sample_movie):
        """Test creating duplicate review from same user."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.0
        )
        
        movie_service.create_review(review_data, user_id=1)
        
        with pytest.raises(ValueError, match="already reviewed"):
            movie_service.create_review(review_data, user_id=1)

    def test_create_review_different_users(self, movie_service, sample_movie):
        """Test multiple users can review same movie."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.0,
            review_text="User 1 review"
        )
        
        review1 = movie_service.create_review(review_data, user_id=1)
        
        review_data.review_text = "User 2 review"
        review2 = movie_service.create_review(review_data, user_id=2)
        
        assert review1.user_id == 1
        assert review2.user_id == 2
        assert review1.id != review2.id

    def test_create_review_rating_boundaries(self, movie_service, sample_movie):
        """Test review creation with boundary ratings."""
        # Minimum rating
        review_min = ReviewCreate(movie_eidr=sample_movie.eidr, rating=1.0)
        created_min = movie_service.create_review(review_min, user_id=1)
        assert created_min.rating == 1.0
        
        # Maximum rating
        review_max = ReviewCreate(movie_eidr=sample_movie.eidr, rating=5.0)
        created_max = movie_service.create_review(review_max, user_id=2)
        assert created_max.rating == 5.0


class TestReviewRetrieval:
    """Test cases for review retrieval."""

    def test_get_movie_reviews_empty(self, movie_service, sample_movie):
        """Test retrieving reviews for movie with no reviews."""
        reviews = movie_service.get_movie_reviews(sample_movie.eidr)
        assert reviews == []

    def test_get_movie_reviews(self, movie_service, sample_movie):
        """Test retrieving reviews for a movie."""
        # Create multiple reviews
        for i in range(3):
            review_data = ReviewCreate(
                movie_eidr=sample_movie.eidr,
                rating=float(i + 3),
                review_text=f"Review {i}"
            )
            movie_service.create_review(review_data, user_id=i + 1)
        
        reviews = movie_service.get_movie_reviews(sample_movie.eidr)
        
        assert len(reviews) == 3
        assert all(r.movie_eidr == sample_movie.eidr for r in reviews)

    def test_get_movie_reviews_pagination(self, movie_service, sample_movie):
        """Test review pagination."""
        # Create 5 reviews
        for i in range(5):
            review_data = ReviewCreate(
                movie_eidr=sample_movie.eidr,
                rating=4.0
            )
            movie_service.create_review(review_data, user_id=i + 1)
        
        # Get first 2 reviews
        reviews_page1 = movie_service.get_movie_reviews(sample_movie.eidr, skip=0, limit=2)
        assert len(reviews_page1) == 2
        
        # Get next 2 reviews
        reviews_page2 = movie_service.get_movie_reviews(sample_movie.eidr, skip=2, limit=2)
        assert len(reviews_page2) == 2
        
        # Verify different reviews
        ids_page1 = {r.id for r in reviews_page1}
        ids_page2 = {r.id for r in reviews_page2}
        assert ids_page1.isdisjoint(ids_page2)

    def test_get_movie_reviews_ordered_by_date(self, movie_service, sample_movie):
        """Test reviews are ordered by creation date (newest first)."""
        import time
        
        review_ids = []
        for i in range(3):
            review_data = ReviewCreate(
                movie_eidr=sample_movie.eidr,
                rating=4.0,
                review_text=f"Review {i}"
            )
            review = movie_service.create_review(review_data, user_id=i + 1)
            review_ids.append(review.id)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        reviews = movie_service.get_movie_reviews(sample_movie.eidr)
        
        # Most recent should be first
        assert reviews[0].id == review_ids[-1]
        assert reviews[-1].id == review_ids[0]

    def test_get_reviews_for_nonexistent_movie(self, movie_service):
        """Test retrieving reviews for non-existent movie."""
        reviews = movie_service.get_movie_reviews("10.5240/NOT-EXIST")
        assert reviews == []


class TestReviewUpdate:
    """Test cases for review updates."""

    def test_update_review_success(self, movie_service, sample_movie):
        """Test successful review update."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=3.0,
            review_text="Initial review"
        )
        review = movie_service.create_review(review_data, user_id=1)
        
        update_data = ReviewUpdate(
            rating=4.5,
            review_text="Updated review"
        )
        updated = movie_service.update_review(review.id, update_data, user_id=1)
        
        assert updated is not None
        assert updated.rating == 4.5
        assert updated.review_text == "Updated review"
        assert updated.updated_at is not None

    def test_update_review_rating_only(self, movie_service, sample_movie):
        """Test updating only rating."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=3.0,
            review_text="Original text"
        )
        review = movie_service.create_review(review_data, user_id=1)
        
        update_data = ReviewUpdate(rating=5.0)
        updated = movie_service.update_review(review.id, update_data, user_id=1)
        
        assert updated.rating == 5.0
        assert updated.review_text == "Original text"

    def test_update_review_text_only(self, movie_service, sample_movie):
        """Test updating only review text."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.0,
            review_text="Original"
        )
        review = movie_service.create_review(review_data, user_id=1)
        
        update_data = ReviewUpdate(review_text="Updated text")
        updated = movie_service.update_review(review.id, update_data, user_id=1)
        
        assert updated.rating == 4.0
        assert updated.review_text == "Updated text"

    def test_update_review_not_found(self, movie_service):
        """Test updating non-existent review."""
        update_data = ReviewUpdate(rating=4.0)
        result = movie_service.update_review(999, update_data, user_id=1)
        
        assert result is None

    def test_update_review_wrong_user(self, movie_service, sample_movie):
        """Test updating review by different user."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=3.0
        )
        review = movie_service.create_review(review_data, user_id=1)
        
        update_data = ReviewUpdate(rating=5.0)
        result = movie_service.update_review(review.id, update_data, user_id=2)
        
        assert result is None

    def test_update_review_updates_timestamp(self, movie_service, sample_movie):
        """Test that update changes the updated_at timestamp."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=3.0
        )
        review = movie_service.create_review(review_data, user_id=1)
        original_updated_at = review.updated_at
        
        import time
        time.sleep(0.1)
        
        update_data = ReviewUpdate(rating=4.0)
        updated = movie_service.update_review(review.id, update_data, user_id=1)
        
        assert updated.updated_at > original_updated_at


class TestReviewDeletion:
    """Test cases for review deletion."""

    def test_delete_review_success(self, movie_service, sample_movie):
        """Test successful review deletion."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.0
        )
        review = movie_service.create_review(review_data, user_id=1)
        
        result = movie_service.delete_review(review.id, user_id=1)
        
        assert result is True
        
        # Verify review is deleted
        reviews = movie_service.get_movie_reviews(sample_movie.eidr)
        assert len(reviews) == 0

    def test_delete_review_not_found(self, movie_service):
        """Test deleting non-existent review."""
        result = movie_service.delete_review(999, user_id=1)
        assert result is False

    def test_delete_review_wrong_user(self, movie_service, sample_movie):
        """Test deleting review by different user."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.0
        )
        review = movie_service.create_review(review_data, user_id=1)
        
        result = movie_service.delete_review(review.id, user_id=2)
        
        assert result is False
        
        # Verify review still exists
        reviews = movie_service.get_movie_reviews(sample_movie.eidr)
        assert len(reviews) == 1

    def test_delete_review_affects_movie_stats(self, movie_service, sample_movie):
        """Test that deleting review updates movie statistics."""
        # Create 2 reviews
        review1_data = ReviewCreate(movie_eidr=sample_movie.eidr, rating=4.0)
        review2_data = ReviewCreate(movie_eidr=sample_movie.eidr, rating=5.0)
        
        review1 = movie_service.create_review(review1_data, user_id=1)
        movie_service.create_review(review2_data, user_id=2)
        
        # Check initial stats
        movie = movie_service.get_movie_by_eidr(sample_movie.eidr)
        assert movie.review_count == 2
        
        # Delete one review
        movie_service.delete_review(review1.id, user_id=1)
        
        # Check updated stats
        movie = movie_service.get_movie_by_eidr(sample_movie.eidr)
        assert movie.review_count == 1


class TestReviewValidation:
    """Test cases for review validation."""

    def test_review_rating_minimum(self, movie_service, sample_movie):
        """Test minimum rating validation."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=1.0
        )
        review = movie_service.create_review(review_data, user_id=1)
        assert review.rating == 1.0

    def test_review_rating_maximum(self, movie_service, sample_movie):
        """Test maximum rating validation."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=5.0
        )
        review = movie_service.create_review(review_data, user_id=1)
        assert review.rating == 5.0

    def test_review_rating_decimal(self, movie_service, sample_movie):
        """Test decimal rating values."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=3.7
        )
        review = movie_service.create_review(review_data, user_id=1)
        assert review.rating == 3.7


class TestMovieReviewStatistics:
    """Test cases for movie review statistics."""

    def test_average_rating_single_review(self, movie_service, sample_movie):
        """Test average rating with single review."""
        review_data = ReviewCreate(
            movie_eidr=sample_movie.eidr,
            rating=4.0
        )
        movie_service.create_review(review_data, user_id=1)
        
        movie = movie_service.get_movie_by_eidr(sample_movie.eidr)
        assert movie.average_rating == 4.0

    def test_average_rating_multiple_reviews(self, movie_service, sample_movie):
        """Test average rating calculation with multiple reviews."""
        ratings = [3.0, 4.0, 5.0]
        for i, rating in enumerate(ratings):
            review_data = ReviewCreate(
                movie_eidr=sample_movie.eidr,
                rating=rating
            )
            movie_service.create_review(review_data, user_id=i + 1)
        
        movie = movie_service.get_movie_by_eidr(sample_movie.eidr)
        expected_avg = sum(ratings) / len(ratings)
        assert movie.average_rating == round(expected_avg, 1)

    def test_review_count(self, movie_service, sample_movie):
        """Test review count property."""
        # Create 3 reviews
        for i in range(3):
            review_data = ReviewCreate(
                movie_eidr=sample_movie.eidr,
                rating=4.0
            )
            movie_service.create_review(review_data, user_id=i + 1)
        
        movie = movie_service.get_movie_by_eidr(sample_movie.eidr)
        assert movie.review_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])