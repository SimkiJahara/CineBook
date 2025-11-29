# app/api/v1/endpoints/auth.py

from typing import Optional, Union, Literal # Added Union and Literal for type hints
from fastapi import APIRouter, Depends, HTTPException, status, Path, Body # Added Path and Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 

# --- Import REAL Components ---
from app.core.security import create_access_token
from app.schemas.token import Token # The Pydantic schema for the response
from app.crud.user import crud_user # The actual CRUD instance
from app.core.dependencies import get_db # The actual DB dependency
from app.schemas.user import (
    UserResponse,
    BuyerCreate, 
    TheatreOwnerCreate 
) # Import creation schemas and response schema
from app.core.config import UserRole # Import the UserRole enum

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


@router.post(
    "/register/{role}", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"]
)
def register_user(
    *,
    db: Session = Depends(get_db),
    # Validate the 'role' path parameter against allowed values
    role: Literal[UserRole.buyer, UserRole.theatre_owner, UserRole.super_admin] = Path(..., title="User Role"),
    # Dynamically select the input schema using the discriminator (the 'role' field in the body)
    user_in: Union[BuyerCreate, TheatreOwnerCreate] = Body(..., discriminator="role")
):
    """
    Register a new user (Buyer or Theatre Owner) using role-specific schemas.
    """
    
    # 1. Check if a user with that email already exists
    if crud_user.get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system."
        )

    # 2. Basic validation check: ensure role in URL path matches role in request body
    if role != user_in.role:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mismatched role in path ('{role}') and request body ('{user_in.role}')."
        )
    
    # 3. Create the user and the associated role model using the unified CRUD function
    # The `crud_user.create_user` method handles which specific role model (Buyer/TheatreOwner) to instantiate.
    user = crud_user.create_user(db, user_in=user_in)

    return user