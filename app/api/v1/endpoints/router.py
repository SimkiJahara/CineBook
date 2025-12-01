"""
User Management Endpoints.

This module provides the API routes for user registration (Buyer, Theatre Owner, Superadmin)
and user retrieval by ID. It handles dependency injection for the database session
and validates user creation data.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD operations and Pydantic schemas
from app.crud.user import  crud_user
# Import the specialized creation schemas
from app.schemas.user import UserResponse, BuyerCreate, TheatreOwnerCreate, SuperadminCreate
# Import database utility function (Dependency for the session)
from app.core.dependencies import get_db

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

    Requires base user fields (email, password) and `fullname`.
    The user is assigned the 'buyer' role upon creation.

    :param user_in: Data required to create a new Buyer user.
    :type user_in: app.schemas.user.BuyerCreate
    :param db: The database session dependency.
    :type db: sqlalchemy.orm.Session
    :raises HTTPException: 409 Conflict if the email is already registered.
    :raises HTTPException: 500 Internal Server Error for unexpected creation issues.
    :return: The newly created User object, including the user's role information.
    :rtype: app.schemas.user.UserResponse
    """
    
    # 1. Check for existing user by email
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        # If user exists, raise a 409 Conflict error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    # 2. Create the new user. The CRUD function handles role-specific creation.
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        # Catch any unexpected database errors during creation
        print(f"Error during Buyer user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Buyer registration due to a server error."
        )

    # 3. Return the created user object
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

    Requires base user fields plus owner-specific fields like `theatre_name` and `license_number`.
    The user is assigned the 'owner' role upon creation.

    :param user_in: Data required to create a new Theatre Owner user.
    :type user_in: app.schemas.user.TheatreOwnerCreate
    :param db: The database session dependency.
    :type db: sqlalchemy.orm.Session
    :raises HTTPException: 409 Conflict if the email is already registered.
    :raises HTTPException: 500 Internal Server Error for unexpected creation issues.
    :return: The newly created User object, including the user's role information.
    :rtype: app.schemas.user.UserResponse
    """
    
    # 1. Check for existing user by email
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        # If user exists, raise a 409 Conflict error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    # 2. Create the new user.
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        # Catch any unexpected database errors during creation
        print(f"Error during Theatre Owner user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Owner registration due to a server error."
        )

    # 3. Return the created user object
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

    This endpoint is typically restricted for initial application setup or internal use.
    The user is assigned the 'admin' role upon creation.

    :param user_in: Data required to create a new Superadmin user.
    :type user_in: app.schemas.user.SuperadminCreate
    :param db: The database session dependency.
    :type db: sqlalchemy.orm.Session
    :raises HTTPException: 409 Conflict if the email is already registered.
    :raises HTTPException: 500 Internal Server Error for unexpected creation issues.
    :return: The newly created User object, including the user's role information.
    :rtype: app.schemas.user.UserResponse
    """
    
    # 1. Check for existing user by email
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        # If user exists, raise a 409 Conflict error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    # 2. Create the new user.
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        # Catch any unexpected database errors during creation
        print(f"Error during Superadmin user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete Superadmin registration due to a server error."
        )

    # 3. Return the created user object
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

    :param user_id: The unique integer ID of the user to retrieve.
    :type user_id: int
    :param db: The database session dependency.
    :type db: sqlalchemy.orm.Session
    :raises HTTPException: 404 Not Found if no user with the given ID exists.
    :return: The User object, including the linked role data (Buyer, Owner, or Admin details).
    :rtype: app.schemas.user.UserResponse
    """
    
    # 1. Fetch user from the database
    db_user = crud_user.get_user(db, user_id=user_id)
    
    # 2. Handle 404 Not Found error
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    # 3. Return the user object
    return db_user