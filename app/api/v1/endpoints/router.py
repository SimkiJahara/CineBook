from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD operations and Pydantic schemas
from app.crud.user import  crud_user
# Import the specialized creation schemas
from app.schemas.user import UserResponse, BuyerCreate, TheatreOwnerCreate 
# Import database utility function (Dependency for the session)
from app.core.dependencies import get_db

# The prefix ensures all endpoints here start with /v1/users (e.g., /v1/users/)
# NOTE: The /v1 part is typically added when including the router in the main app
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# The prefix ensures all endpoints here start with /v1/users (e.g., /v1/users/)
# NOTE: The /v1 part is typically added when including the router in the main app
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
    Registers a **Buyer** user. Requires only base user fields and `fullname`.
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
    Registers a **Theatre Owner** user. Requires base user fields plus owner-specific fields.
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


### 3. Read User Endpoint (`GET /users/{user_id}`)
# ... (The rest of the file remains the same)





### 2. Read User Endpoint (`GET /users/{user_id}`)

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
    Retrieves a user by ID, including all nested role details (e.g., the nested `theaters` list 
    for a TheaterOwner) using SQLAlchemy's relationships.
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
    # FastAPI/Pydantic converts the ORM model to the UserResponse schema, 
    # leveraging from_attributes=True to include nested relationships.
    return db_user