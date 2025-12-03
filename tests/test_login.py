# tests/test_login.py
from fastapi import status
from app.core.security import get_password_hash #
from app.models.user import User #

# 1. TEST SUCCESS SCENARIO
def test_login_success(client, db_session):
    """
    Scenario: A valid user exists. We send correct credentials.
    Expectation: 200 OK and a Bearer token in the response.
    """
    # -- ARRANGE: Create a dummy user in the test database --
    password = "securepassword123"
    hashed_pwd = get_password_hash(password)
    
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=hashed_pwd,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # -- ACT: Attempt to login --
    # Note: OAuth2PasswordRequestForm expects form data (data=...), not JSON (json=...)
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": password}
    )

    # -- ASSERT: Check the results --
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# 2. TEST FAILURE (WRONG PASSWORD)
def test_login_wrong_password(client, db_session):
    """
    Scenario: User exists, but we send the wrong password.
    Expectation: 401 Unauthorized.
    """
    # -- ARRANGE --
    password = "correctpassword"
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash(password),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # -- ACT --
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )

    # -- ASSERT --
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

# 3. TEST FAILURE (USER NOT FOUND)
def test_login_user_not_found(client, db_session):
    """
    Scenario: We try to login with a username that does not exist in the DB.
    Expectation: 401 Unauthorized.
    """
    # -- ARRANGE --
    # We do NOT add any user to the db_session here. Database is empty.

    # -- ACT --
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "ghost_user", "password": "any_password"}
    )

    # -- ASSERT --
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"