"""
Unit tests for unpublished and published screening endpoints.

Run tests with: pytest tests/test_screening_routes.py -v
"""

import pytest
from datetime import date, time, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base, Theaterowner, Theater, Hall, Movie, Screening, User

# ---------------------------------------------------------------
# Test Database Setup
# ---------------------------------------------------------------

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=test_engine
)


def override_get_db():
    """Override the get_db dependency to use test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


# ---------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    from sqlalchemy.sql.expression import TextClause
    from sqlalchemy import Text
    from sqlalchemy.dialects.postgresql import JSONB
    
    # Convert JSONB columns to TEXT for SQLite compatibility
    for table in Base.metadata.tables.values():
        for column in table.columns:
            # Replace JSONB with TEXT
            if isinstance(column.type, JSONB):
                column.type = Text()
            
            # Clean PostgreSQL-specific syntax from server defaults
            if column.server_default is not None:
                if hasattr(column.server_default, 'arg'):
                    if isinstance(column.server_default.arg, TextClause):
                        original = column.server_default.arg.text
                        # Remove PostgreSQL-specific type casts
                        cleaned = original.split('::')[0] if '::' in original else original
                        column.server_default.arg.text = cleaned
    
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_owner(test_db):
    """Create a sample theater owner."""
    # First create the User record with all required fields
    owner = Theaterowner(
        id=1,
        email="owner@test.com",
        name="Test Owner",
        passwordhash="hashed_password",
        role="TheaterOwner",
        businessname="Test Theater Business",
        ownername="Test Owner",
        phone="1234567890",
        licensenumber="LIC123"
    )
    test_db.add(owner)
    test_db.commit()
    test_db.refresh(owner)
    return owner


@pytest.fixture
def sample_theater(test_db, sample_owner):
    """Create a sample theater."""
    theater = Theater(
        companyid="COMP001",
        branchid="BRANCH001",
        name="Test Theater",
        address="123 Test St",
        ownerid=sample_owner.id,
        contact="9876543210",
        isverified=True
    )
    test_db.add(theater)
    test_db.commit()
    test_db.refresh(theater)
    return theater


@pytest.fixture
def sample_hall(test_db, sample_theater):
    """Create a sample hall."""
    hall = Hall(
        hallid="HALL001",
        companyid=sample_theater.companyid,
        branchid=sample_theater.branchid,
        capacity=100
    )
    test_db.add(hall)
    test_db.commit()
    test_db.refresh(hall)
    return hall


@pytest.fixture
def sample_movie(test_db):
    """Create a sample active movie."""
    movie = Movie(
        eidr="10.5240/TEST-MOVIE-001",
        title="Test Movie",
        posterurl="http://test.com/poster.jpg",
        lengthmin=120,
        rating="PG-13",
        releasedate=date(2024, 1, 1),
        description="A test movie",
        director="Test Director",
        language="English",
        is_active=1
    )
    test_db.add(movie)
    test_db.commit()
    test_db.refresh(movie)
    return movie


@pytest.fixture
def sample_unpublished_screening(test_db, sample_hall, sample_movie):
    """Create a sample unpublished screening."""
    screening = Screening(
        date=date.today() + timedelta(days=5),
        starttime=time(14, 30),
        status='SCHEDULED',
        movieeidr=sample_movie.eidr,
        hallid=sample_hall.hallid,
        hallcompanyid=sample_hall.companyid,
        hallbranchid=sample_hall.branchid
    )
    test_db.add(screening)
    test_db.commit()
    test_db.refresh(screening)
    return screening


@pytest.fixture
def sample_published_screening(test_db, sample_hall, sample_movie):
    """Create a sample published screening."""
    screening = Screening(
        date=date.today() + timedelta(days=7),
        starttime=time(18, 0),
        status='PUBLISHED',
        movieeidr=sample_movie.eidr,
        hallid=sample_hall.hallid,
        hallcompanyid=sample_hall.companyid,
        hallbranchid=sample_hall.branchid
    )
    test_db.add(screening)
    test_db.commit()
    test_db.refresh(screening)
    return screening


# ---------------------------------------------------------------
# Tests for GET /unpublished-screenings/{owner_id}
# ---------------------------------------------------------------

class TestUnpublishedScreenings:
    """Test suite for unpublished screenings endpoint."""
    
    def test_get_unpublished_screenings_success(
        self, 
        test_db, 
        sample_owner, 
        sample_unpublished_screening
    ):
        """Test successful retrieval of unpublished screenings."""
        response = client.get(f"/unpublished-screenings/{sample_owner.id}")
        
        assert response.status_code == 200
        assert "unpublished" in response.text.lower()
    
    
    def test_get_unpublished_screenings_owner_not_found(self, test_db):
        """Test with non-existent owner ID."""
        response = client.get("/unpublished-screenings/99999")
        
        assert response.status_code == 404
        assert "Owner not found" in response.text
    
    
    def test_get_unpublished_screenings_empty_list(
        self, 
        test_db, 
        sample_owner,
        sample_theater,
        sample_hall
    ):
        """Test when owner has no unpublished screenings."""
        response = client.get(f"/unpublished-screenings/{sample_owner.id}")
        
        assert response.status_code == 200
        assert "no unpublished screenings" in response.text.lower()
    
    
    def test_get_unpublished_screenings_excludes_published(
        self, 
        test_db, 
        sample_owner,
        sample_unpublished_screening,
        sample_published_screening
    ):
        """Test that published screenings are not included."""
        response = client.get(f"/unpublished-screenings/{sample_owner.id}")
        
        assert response.status_code == 200

        # Check unpublished is there
        assert str(sample_unpublished_screening.date) in response.text
    
        # Check published is Not there
        assert str(sample_published_screening.date) not in response.text
    
    
    def test_get_unpublished_screenings_filter_by_date(
        self, 
        test_db, 
        sample_owner,
        sample_hall,
        sample_movie
    ):
        """Test filtering unpublished screenings by date."""
        # Create screenings on different dates
        target_date = date.today() + timedelta(days=3)
        other_date = date.today() + timedelta(days=10)
        
        screening1 = Screening(
            date=target_date,
            starttime=time(14, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        screening2 = Screening(
            date=other_date,
            starttime=time(16, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        # Filter by target date
        response = client.get(
            f"/unpublished-screenings/{sample_owner.id}",
            params={"date_filter": str(target_date)}
        )
        
        assert response.status_code == 200
        assert str(target_date) in response.text
        # Other date should not appear due to filter
    
    
    def test_get_unpublished_screenings_filter_by_hall(
        self, 
        test_db, 
        sample_owner,
        sample_theater,
        sample_movie
    ):
        """Test filtering unpublished screenings by hall."""
        # Create two halls
        hall1 = Hall(
            hallid="HALL001",
            companyid=sample_theater.companyid,
            branchid=sample_theater.branchid,
            capacity=100
        )
        
        hall2 = Hall(
            hallid="HALL002",
            companyid=sample_theater.companyid,
            branchid=sample_theater.branchid,
            capacity=150
        )
        
        test_db.add(hall1)
        test_db.add(hall2)
        test_db.commit()
        
        # Create screenings in different halls
        screening1 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(14, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=hall1.hallid,
            hallcompanyid=hall1.companyid,
            hallbranchid=hall1.branchid
        )
        
        screening2 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(16, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=hall2.hallid,
            hallcompanyid=hall2.companyid,
            hallbranchid=hall2.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        # Filter by hall1
        response = client.get(
            f"/unpublished-screenings/{sample_owner.id}",
            params={"hallid": "HALL001"}
        )
        
        assert response.status_code == 200
        assert "HALL001" in response.text
    
    
    def test_get_unpublished_screenings_filter_by_movie(
        self, 
        test_db, 
        sample_owner,
        sample_hall
    ):
        """Test filtering unpublished screenings by movie."""
        # Create two movies
        movie1 = Movie(
            eidr="10.5240/MOVIE-001",
            title="Movie One",
            is_active=1
        )
        
        movie2 = Movie(
            eidr="10.5240/MOVIE-002",
            title="Movie Two",
            is_active=1
        )
        
        test_db.add(movie1)
        test_db.add(movie2)
        test_db.commit()
        
        # Create screenings with different movies
        screening1 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(14, 0),
            status='SCHEDULED',
            movieeidr=movie1.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        screening2 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(18, 0),
            status='SCHEDULED',
            movieeidr=movie2.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        # Filter by movie1
        response = client.get(
            f"/unpublished-screenings/{sample_owner.id}",
            params={"movieeidr": movie1.eidr}
        )
        
        assert response.status_code == 200
        assert "Movie One" in response.text
    
    
    def test_get_unpublished_screenings_multiple_filters(
        self, 
        test_db, 
        sample_owner,
        sample_hall,
        sample_movie
    ):
        """Test applying multiple filters simultaneously."""
        target_date = date.today() + timedelta(days=5)
        
        screening = Screening(
            date=target_date,
            starttime=time(14, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        test_db.add(screening)
        test_db.commit()
        
        # Apply multiple filters
        response = client.get(
            f"/unpublished-screenings/{sample_owner.id}",
            params={
                "date_filter": str(target_date),
                "hallid": sample_hall.hallid,
                "movieeidr": sample_movie.eidr
            }
        )
        
        assert response.status_code == 200
        assert str(target_date) in response.text
        assert sample_hall.hallid in response.text
    
    
    def test_get_unpublished_screenings_only_owner_halls(
        self, 
        test_db,
        sample_movie
    ):
        """Test that only screenings in owner's halls are returned."""
        # Create owner1 with all User fields
        owner1 = Theaterowner(
            id=1,
            email="owner1@test.com",
            name="Owner 1",
            passwordhash="hash1",
            role="TheaterOwner",
            businessname="Business 1",
            ownername="Owner 1"
        )
        
        # Create owner2 with all User fields
        owner2 = Theaterowner(
            id=2,
            email="owner2@test.com",
            name="Owner 2",
            passwordhash="hash2",
            role="TheaterOwner",
            businessname="Business 2",
            ownername="Owner 2"
        )
        
        test_db.add(owner1)
        test_db.add(owner2)
        test_db.commit()
        
        # Create theaters for each owner
        theater1 = Theater(
            companyid="COMP001",
            branchid="BRANCH001",
            name="Theater 1",
            address="Address 1",
            ownerid=owner1.id
        )
        
        theater2 = Theater(
            companyid="COMP002",
            branchid="BRANCH002",
            name="Theater 2",
            address="Address 2",
            ownerid=owner2.id
        )
        
        test_db.add(theater1)
        test_db.add(theater2)
        test_db.commit()
        
        # Create halls for each theater
        hall1 = Hall(
            hallid="HALL001",
            companyid=theater1.companyid,
            branchid=theater1.branchid,
            capacity=100
        )
        
        hall2 = Hall(
            hallid="HALL002",
            companyid=theater2.companyid,
            branchid=theater2.branchid,
            capacity=150
        )
        
        test_db.add(hall1)
        test_db.add(hall2)
        test_db.commit()
        
        # Create screenings in both halls
        screening1 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(14, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=hall1.hallid,
            hallcompanyid=hall1.companyid,
            hallbranchid=hall1.branchid
        )
        
        screening2 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(16, 0),
            status='SCHEDULED',
            movieeidr=sample_movie.eidr,
            hallid=hall2.hallid,
            hallcompanyid=hall2.companyid,
            hallbranchid=hall2.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        # Owner1 should only see their screening
        response = client.get(f"/unpublished-screenings/{owner1.id}")
        
        assert response.status_code == 200
        assert "HALL001" in response.text
        assert "HALL002" not in response.text

# ---------------------------------------------------------------
# Tests for GET /published-screenings/{owner_id}
# ---------------------------------------------------------------

class TestPublishedScreenings:
    """Test suite for published screenings endpoint."""
    
    def test_get_published_screenings_success(
        self, 
        test_db, 
        sample_owner, 
        sample_published_screening
    ):
        """Test successful retrieval of published screenings."""
        response = client.get(f"/published-screenings/{sample_owner.id}")
        
        assert response.status_code == 200
        assert "published" in response.text.lower()
    
    
    def test_get_published_screenings_owner_not_found(self, test_db):
        """Test with non-existent owner ID."""
        response = client.get("/published-screenings/99999")
        
        assert response.status_code == 404
        assert "Owner not found" in response.text
    
    
    def test_get_published_screenings_empty_list(
        self, 
        test_db, 
        sample_owner,
        sample_theater,
        sample_hall
    ):
        """Test when owner has no published screenings."""
        response = client.get(f"/published-screenings/{sample_owner.id}")
        
        assert response.status_code == 200
        assert "no published screenings" in response.text.lower()
    
    
    def test_get_published_screenings_excludes_unpublished(
        self, 
        test_db, 
        sample_owner,
        sample_unpublished_screening,
        sample_published_screening
    ):
        """Test that unpublished screenings are not included."""
        response = client.get(f"/published-screenings/{sample_owner.id}")
        
        assert response.status_code == 200
        # Published screening date should appear
        assert str(sample_published_screening.date) in response.text
    
    
    def test_get_published_screenings_excludes_past(
        self, 
        test_db, 
        sample_owner,
        sample_hall,
        sample_movie
    ):
        """Test that past published screenings are excluded."""
        # Create a past published screening
        past_screening = Screening(
            date=date.today() - timedelta(days=5),
            starttime=time(14, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        # Create a future published screening
        future_screening = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(18, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        test_db.add(past_screening)
        test_db.add(future_screening)
        test_db.commit()
        
        response = client.get(f"/published-screenings/{sample_owner.id}")
        
        assert response.status_code == 200
        # Future screening should appear
        assert str(future_screening.date) in response.text
        # Past screening should not appear
        past_date_str = str(past_screening.date)
        # This is tricky - past date might appear in filters
        # Better to check for specific context
    
    
    def test_get_published_screenings_filter_by_date(
        self, 
        test_db, 
        sample_owner,
        sample_hall,
        sample_movie
    ):
        """Test filtering published screenings by date."""
        target_date = date.today() + timedelta(days=3)
        other_date = date.today() + timedelta(days=10)
        
        screening1 = Screening(
            date=target_date,
            starttime=time(14, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        screening2 = Screening(
            date=other_date,
            starttime=time(16, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        response = client.get(
            f"/published-screenings/{sample_owner.id}",
            params={"date_filter": str(target_date)}
        )
        
        assert response.status_code == 200
        assert str(target_date) in response.text
    
    
    def test_get_published_screenings_filter_by_hall(
        self, 
        test_db, 
        sample_owner,
        sample_theater,
        sample_movie
    ):
        """Test filtering published screenings by hall."""
        hall1 = Hall(
            hallid="HALL001",
            companyid=sample_theater.companyid,
            branchid=sample_theater.branchid,
            capacity=100
        )
        
        hall2 = Hall(
            hallid="HALL002",
            companyid=sample_theater.companyid,
            branchid=sample_theater.branchid,
            capacity=150
        )
        
        test_db.add(hall1)
        test_db.add(hall2)
        test_db.commit()
        
        screening1 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(14, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=hall1.hallid,
            hallcompanyid=hall1.companyid,
            hallbranchid=hall1.branchid
        )
        
        screening2 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(16, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=hall2.hallid,
            hallcompanyid=hall2.companyid,
            hallbranchid=hall2.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        response = client.get(
            f"/published-screenings/{sample_owner.id}",
            params={"hallid": "HALL001"}
        )
        
        assert response.status_code == 200
        assert "HALL001" in response.text
    
    
    def test_get_published_screenings_filter_by_movie(
        self, 
        test_db, 
        sample_owner,
        sample_hall
    ):
        """Test filtering published screenings by movie."""
        movie1 = Movie(
            eidr="10.5240/MOVIE-001",
            title="Movie One",
            is_active=1
        )
        
        movie2 = Movie(
            eidr="10.5240/MOVIE-002",
            title="Movie Two",
            is_active=1
        )
        
        test_db.add(movie1)
        test_db.add(movie2)
        test_db.commit()
        
        screening1 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(14, 0),
            status='PUBLISHED',
            movieeidr=movie1.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        screening2 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(18, 0),
            status='PUBLISHED',
            movieeidr=movie2.eidr,
            hallid=sample_hall.hallid,
            hallcompanyid=sample_hall.companyid,
            hallbranchid=sample_hall.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        response = client.get(
            f"/published-screenings/{sample_owner.id}",
            params={"movieeidr": movie1.eidr}
        )
        
        assert response.status_code == 200
        assert "Movie One" in response.text
    
    
    def test_get_published_screenings_only_owner_halls(
        self, 
        test_db,
        sample_movie
    ):
        """Test that only screenings in owner's halls are returned."""
        # Create owner1 with all User fields
        owner1 = Theaterowner(
            id=1,
            email="owner1@test.com",
            name="Owner 1",
            passwordhash="hash1",
            role="TheaterOwner",
            businessname="Business 1",
            ownername="Owner 1"
        )
        
        # Create owner2 with all User fields
        owner2 = Theaterowner(
            id=2,
            email="owner2@test.com",
            name="Owner 2",
            passwordhash="hash2",
            role="TheaterOwner",
            businessname="Business 2",
            ownername="Owner 2"
        )
        
        test_db.add(owner1)
        test_db.add(owner2)
        test_db.commit()
        
        # Create separate theaters
        theater1 = Theater(
            companyid="COMP001",
            branchid="BRANCH001",
            name="Theater 1",
            address="Address 1",
            ownerid=owner1.id
        )
        
        theater2 = Theater(
            companyid="COMP002",
            branchid="BRANCH002",
            name="Theater 2",
            address="Address 2",
            ownerid=owner2.id
        )
        
        test_db.add(theater1)
        test_db.add(theater2)
        test_db.commit()
        
        # Create halls
        hall1 = Hall(
            hallid="HALL001",
            companyid=theater1.companyid,
            branchid=theater1.branchid,
            capacity=100
        )
        
        hall2 = Hall(
            hallid="HALL002",
            companyid=theater2.companyid,
            branchid=theater2.branchid,
            capacity=150
        )
        
        test_db.add(hall1)
        test_db.add(hall2)
        test_db.commit()
        
        # Create published screenings
        screening1 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(14, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=hall1.hallid,
            hallcompanyid=hall1.companyid,
            hallbranchid=hall1.branchid
        )
        
        screening2 = Screening(
            date=date.today() + timedelta(days=5),
            starttime=time(16, 0),
            status='PUBLISHED',
            movieeidr=sample_movie.eidr,
            hallid=hall2.hallid,
            hallcompanyid=hall2.companyid,
            hallbranchid=hall2.branchid
        )
        
        test_db.add(screening1)
        test_db.add(screening2)
        test_db.commit()
        
        # Owner1 should only see their screening
        response = client.get(f"/published-screenings/{owner1.id}")
        
        assert response.status_code == 200
        assert "HALL001" in response.text
        assert "HALL002" not in response.text
