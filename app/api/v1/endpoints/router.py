from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD operations and Pydantic schemas
from app.crud.user import  crud_user
from app.schemas.user import UserCreate, UserResponse
# Import database utility function (Dependency for the session)
# NOTE: The dependency function is assumed to be defined in app/core/dependencies.py
from app.core.dependencies import get_db

# The prefix ensures all endpoints here start with /v1/users (e.g., /v1/users/)
# NOTE: The /v1 part is typically added when including the router in the main app
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)



### 1. Register User Endpoint (`POST /users/`)

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new User (Buyer, TheaterOwner, or Superadmin)",
)
def create_new_user(
    user_in: UserCreate, # Pydantic schema handles input validation
    db: Session = Depends(get_db) # Dependency Injection for SQLAlchemy session
):
    """
    Handles **synchronous** user registration. 
    Checks if a user with the given email already exists before creating.
    """
    
    # 1. Check for existing user by email
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        # If user exists, raise a 409 Conflict error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    # 2. Create the new user and specialized role entry
    # The CRUD function handles hashing the password and committing the transaction.
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        # Catch any unexpected database errors during creation (e.g., schema validation errors)
        print(f"Error during user creation: {e}")
        # Raising a generic 500 error for unhandled internal issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete user registration due to a server error."
        )

    # 3. Return the created user object
    return new_user



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