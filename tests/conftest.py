import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db

SQLALCHEMY_DATABASE_URL= "sqlite:///:memory:"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
poolclass = StaticPool,)

#creating a session for testing
TestingSessionLocal = sessionmaker(autocommit= False, autoflush = False, bind= engine)

#creating fixture for database section
@pytest.fixture(scope= "function")
def db_session():
    """Creates a fresh database"""
    Base.metadata.create_all(bind=engine)

    db= TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind= engine)


#fixture for test client

@pytest.fixture(scope="function")
def client(db_session):
    """Creates a test client that uses the overriden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

            
    app.dependency_overrides[get_db] =override_get_db
    

    with TestClient(app) as c:
        yield c


    app.dependency_overrides.clear()