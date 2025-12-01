"""
User Management Endpoints.

This module provides the API routes for user registration (Buyer, Theatre Owner, Superadmin)
and user retrieval by ID.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# NOTE: Assuming these imports are correct based on your project structure
from app.crud.user import  crud_user
from app.schemas.user import UserResponse, BuyerCreate, TheatreOwnerCreate, SuperadminCreate
from app.core.db import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

### 1. Register Buyer Endpoint (`POST /users/buyer`)

@router.post(
    "/buyer",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Buyer user",
)
def register_buyer(
    user_in: BuyerCreate, # Uses the specialized BuyerCreate schema
    db: Session = Depends(get_db)
):
    """
    Registers a **Buyer** user.

    :param user_in: The user data for the new Buyer, containing email, password, and
        specific buyer details.
    :param db: The SQLAlchemy database session.
    :raises HTTPException: 409 Conflict if the email is already registered.
    :raises HTTPException: 500 Internal Server Error on database failure.
    :returns: The newly created user object, including the assigned role.
    """
    
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        print(f"Error during Buyer user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Buyer registration due to a server error."
        )

    return new_user


### 2. Register Theatre Owner Endpoint (`POST /users/owner`)

@router.post(
    "/owner",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Theatre Owner user",
)
def register_theatre_owner(
    user_in: TheatreOwnerCreate, # Uses the specialized TheatreOwnerCreate schema
    db: Session = Depends(get_db)
):
    """
    Registers a **Theatre Owner** user.

    :param user_in: The user data for the new Theatre Owner.
    :param db: The SQLAlchemy database session.
    :raises HTTPException: 409 Conflict if the email is already registered.
    :raises HTTPException: 500 Internal Server Error on database failure.
    :returns: The newly created user object, including the assigned role.
    """
    
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        print(f"Error during Theatre Owner user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Owner registration due to a server error."
        )

    return new_user


### 3. Register Superadmin Endpoint (`POST /users/admin`)

@router.post(
    "/admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Superadmin user",
)
def register_superadmin(
    user_in: SuperadminCreate, # Uses the specialized SuperadminCreate schema
    db: Session = Depends(get_db)
):
    """
    Registers a **Superadmin** user.

    :param user_in: The user data for the new Superadmin.
    :param db: The SQLAlchemy database session.
    :raises HTTPException: 409 Conflict if the email is already registered.
    :raises HTTPException: 500 Internal Server Error on database failure.
    :returns: The newly created user object, including the assigned role.
    """
    
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        print(f"Error during Superadmin user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Superadmin registration due to a server error."
        )

    return new_user


### 4. Read User Endpoint (`GET /users/{user_id}`)

@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="Retrieve a User by ID with their specialized role data",
)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieves a user by ID, including all nested role details using SQLAlchemy's relationships.

    :param user_id: The ID of the user to retrieve.
    :param db: The SQLAlchemy database session.
    :raises HTTPException: 404 Not Found if the user does not exist.
    :returns: The user object, including their associated role data.
    """
    
    db_user = crud_user.get_user(db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    return db_user