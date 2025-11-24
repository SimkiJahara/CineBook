from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

# Assuming security functions are available from a file one level up and in core
from app.core.security import create_access_token, verify_password

# --- Mock Schemas (These would typically be in app.schemas) ---

class Token(BaseModel):
    """Schema for the returned JWT token."""
    access_token: str
    token_type: str = "bearer"

class UserInDB(BaseModel):
    """Internal model representing a user record from the database."""
    id: int = 1
    email: str
    hashed_password: str
    is_active: bool = True

    class Config:
        # Allow accessing fields like dictionary keys
        from_attributes = True

# --- Mock CRUD User Logic (These would typically be in app.crud) ---
# Simulates the database interaction for user authentication.
class MockCRUDUser:
    """Simulated CRUD operations for the User model."""
    def authenticate_user(self, db: Any, email: str, password: str) -> Optional[UserInDB]:
        """
        Authenticates a user by email and password.

        NOTE: 'db' parameter is purely illustrative of a dependency.
        """
        # In a real app, you would fetch the user by 'email' from the DB.
        # This mocks a user found in the DB.
        if email == "admin@cinebook.com":
            # NOTE: Use get_password_hash("supersecret") to generate this hash
            mock_hash = "$2b$12$Kk27eY5P.34.F/qM7iO70.K6w40m.K3l4N9B7Z/T4f4u3w8D6v4o." # Hashed "supersecret"
            user_in_db = UserInDB(id=1, email=email, hashed_password=mock_hash)

            if not user_in_db.is_active:
                return None # User is inactive

            if verify_password(password, user_in_db.hashed_password):
                return user_in_db
        
        return None # Authentication failed

# Dependency to simulate the CRUD object and the DB session
crud_user = MockCRUDUser()
def get_db():
    """Mock database dependency (yields a placeholder value)."""
    # In a real app, this would yield a SQLAlchemy/other DB session
    yield {"session": "mock"}

# --- FastAPI Router ---

router = APIRouter()

@router.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    db: Any = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login endpoint.

    Uses the username (which is the email) and password from the form data
    to verify credentials and returns an access token.
    """
    # 1. Authenticate the user
    user = crud_user.authenticate_user(
        db,
        email=form_data.username, # OAuth2PasswordRequestForm uses 'username' for the user identifier
        password=form_data.password
    )

    if not user:
        # 2. Raise exception if authentication fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create the JWT token
    # We use the user's ID as the 'sub' (subject) of the JWT for identification
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )

    # 4. Return the standard Token response
    return Token(access_token=access_token, token_type="bearer")