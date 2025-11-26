# app/api/v1/endpoints/auth.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session # Added Session import

# --- Import REAL Components ---
from app.core.security import create_access_token
from app.schemas.token import Token # The Pydantic schema for the response
from app.crud.user import crud_user # The actual CRUD instance
from app.core.dependencies import get_db # The actual DB dependency


# --- FastAPI Router ---

router = APIRouter()

@router.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    db: Session = Depends(get_db), # Use the actual DB dependency
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login endpoint.

    Uses the username (which is the email) and password from the form data
    to verify credentials and returns an access token.
    """
    # 1. Authenticate the user (using the REAL crud_user and DB session)
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
    # We use the user's email and ID as the payload data
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )

    # 4. Return the standard Token response
    return Token(access_token=access_token, token_type="bearer")