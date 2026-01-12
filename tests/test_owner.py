from fastapi import status
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

# Helper function to create a user, assign a role, and get their token
def get_auth_headers(client, db_session, username, role_name=None):
    password = "password123"
    hashed_pwd = get_password_hash(password)
    
    # 1. Create User
    user = User(
        username=username,
        email=f"{username}@example.com",
        full_name=f"{username} Test",
        hashed_password=hashed_pwd,
        is_active=True
    )
    
    # 2. Create and Assign Role if provided
    if role_name:
        # Check if role exists first (to avoid duplicates in test DB)
        role = db_session.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name} role")
            db_session.add(role)
        
        user.roles.append(role)
    
    db_session.add(user)
    db_session.commit()
    
    # 3. Login to get token
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 1. TEST OWNER ACCESS (Should Succeed)
def test_owner_dashboard_access(client, db_session):
    """
    Scenario: User has 'theatre_owner' role.
    Expectation: 200 OK and welcome message.
    """
    # -- ARRANGE --
    headers = get_auth_headers(
        client, 
        db_session, 
        username="owner_user", 
        role_name="theatre_owner"
    )

    # -- ACT --
    response = client.get("/api/v1/owner/", headers=headers)

    # -- ASSERT --
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome Owner"}

# 2. TEST REGULAR USER ACCESS (Should Fail - 403 Forbidden)
def test_owner_dashboard_forbidden(client, db_session):
    """
    Scenario: User has 'user' role (NOT 'theatre_owner').
    Expectation: 403 Forbidden.
    """
    # -- ARRANGE --
    headers = get_auth_headers(
        client, 
        db_session, 
        username="regular_user", 
        role_name="user"
    )

    # -- ACT --
    response = client.get("/api/v1/owner/", headers=headers)

    # -- ASSERT --
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not enough permissions. Theatre Owner role required."

# 3. TEST UNAUTHENTICATED ACCESS (Should Fail - 401 Unauthorized)
def test_owner_dashboard_unauthorized(client):
    """
    Scenario: No Authorization header provided.
    Expectation: 401 Unauthorized.
    """
    # -- ACT --
    response = client.get("/api/v1/owner/")

    # -- ASSERT --
    assert response.status_code == status.HTTP_401_UNAUTHORIZED