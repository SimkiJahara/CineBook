# tests/test_register.py
from fastapi import status

# 1. TEST SUCCESSFUL REGISTRATION
def test_register_user_success(client):
    """
    Scenario: valid username, email, and strong password.
    Expectation: 201 Created, and response contains username/email (but NO password).
    """
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "full_name": "New User",
        "password": "strongpassword123"
    }
    
    response = client.post("/api/v1/users/register", json=payload)

    # Assert creation success
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    
    # SECURITY ASSERTION: Ensure password is NOT returned in the response
    assert "password" not in data
    assert "hashed_password" not in data

# 2. TEST DUPLICATE USERNAME
def test_register_duplicate_username(client):
    """
    Scenario: Register 'user1', then try to register 'user1' again.
    Expectation: 400 Bad Request.
    """
    # Step 1: Create the first user
    payload = {
        "username": "unique_user",
        "email": "unique@example.com",
        "full_name": "First Entry",
        "password": "password123"
    }
    client.post("/api/v1/users/register", json=payload)

    # Step 2: Try to create the exact same username again (even with diff email)
    payload_duplicate = payload.copy()
    payload_duplicate["email"] = "other@example.com" # Diff email, same username
    
    response = client.post("/api/v1/users/register", json=payload_duplicate)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already registered"

# 3. TEST DUPLICATE EMAIL
def test_register_duplicate_email(client):
    """
    Scenario: Register with 'mail@test.com', then try using that email again.
    Expectation: 400 Bad Request.
    """
    # Step 1: Create first user
    payload = {
        "username": "user_a",
        "email": "shared@example.com",
        "full_name": "User A",
        "password": "password123"
    }
    client.post("/api/v1/users/register", json=payload)

    # Step 2: Try to register different username but SAME email
    payload_duplicate = {
        "username": "user_b", # Different username
        "email": "shared@example.com", # SAME EMAIL
        "full_name": "User B",
        "password": "password123"
    }
    
    response = client.post("/api/v1/users/register", json=payload_duplicate)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

# 4. TEST PASSWORD VALIDATION (TOO SHORT)
def test_register_weak_password(client):
    """
    Scenario: Password is '123' (less than 8 chars).
    Expectation: 422 Unprocessable Entity (Pydantic validation error).
    """
    payload = {
        "username": "weak_user",
        "email": "weak@example.com",
        "full_name": "Weak Password User",
        "password": "123" # Too short!
    }
    
    response = client.post("/api/v1/users/register", json=payload)

    # Note: Validation errors return 422, not 400
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Optional: Check that the error message mentions the password field
    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "password" for error in errors)