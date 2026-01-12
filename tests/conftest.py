import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db

# 1. SETUP TEST DATABASE
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. FIXTURE: DATABASE SESSION
@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# 3. FIXTURE: TEST CLIENT
@pytest.fixture(scope="function")
def client(db_session):
    """Creates a test client that uses the overridden database dependency."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            # FIXED: We do NOT close the session here. 
            # The 'db_session' fixture above handles closing it after the test finishes.
            pass 

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()