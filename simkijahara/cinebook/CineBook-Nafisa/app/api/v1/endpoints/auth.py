from typing import Optional, Union, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 

# --- Import REAL Components ---
from app.core.security import create_access_token
from app.schemas.token import Token 
from app.crud.user import crud_user 
from app.core.db import get_db 
from app.schemas.user import (
    UserResponse,
    BuyerCreate, 
    TheatreOwnerCreate 
) 
from app.core.config import UserRole 

# --- FastAPI Router ---

router = APIRouter()
# ------------------------
# 1. MODULE DOCSTRING
# ------------------------
"""
Authentication Endpoints

This module defines the API endpoints for user authentication, including 
token generation and new user registration for different roles.
"""

@router.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Retrieves an OAuth2 access token upon successful authentication.

    This endpoint takes a user's email (as username) and password, 
    verifies the credentials, and issues a JWT access token.

    Args:
        db: The SQLAlchemy database session dependency.
        form_data: The standard OAuth2 password request form data (contains username/password).

    Returns:
        Token: A Pydantic object containing the generated access token and type ("bearer").

    Raises:
        HTTPException: If the email or password provided is incorrect (HTTP 401 Unauthorized).
    """
    # 1. Authenticate the user (using the REAL crud_user and DB session)
    user = crud_user.authenticate_user(
        db,
        email=form_data.username, 
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
    Registers a new user in the database.

    The registration process is tailored based on the user's role (Buyer or Theatre Owner),
    ensuring role-specific data is correctly validated and stored.

    Args:
        db: The SQLAlchemy database session dependency.
        role: The user role specified in the URL path. Must be one of the allowed UserRole enum values.
        user_in: The user registration data. Must match the schema for the specified 'role'.

    Returns:
        UserResponse: The newly created user object (includes public information only).

    Raises:
        HTTPException: 
            - If a user with the provided email already exists (HTTP 400 Bad Request).
            - If the role in the URL path does not match the role in the request body (HTTP 400 Bad Request).
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
    user = crud_user.create_user(db, user_in=user_in)

    return user
