from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD operations and Pydantic schemas
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserResponse
# Import database utility function (assuming you have a dependency for the session)
# NOTE: The dependency function is assumed to be defined in app/core/dependencies.py
from app.core.dependencies import get_db

# The prefix ensures all endpoints here start with /v1/users (e.g., /v1/users/)
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


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
    Handles user registration. 
    Checks if a user with the given email already exists before creating.
    The single `UserCreate` schema manages input for both the base `User` 
    and the specialized role model (Buyer/TheaterOwner/Superadmin) based on the `role` field.
    """
    
    # 1. Check for existing user
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        # If user exists, raise a conflict error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
        
    # 2. Create user and specialized role entry
    try:
        new_user = crud_user.create_user(db, user_in=user_in)
    except Exception as e:
        # Catch any unexpected database errors during creation
        print(f"Error during user creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete user registration due to a server error."
        )

    # 3. Return the created user object, which FastAPI converts to UserResponse
    return new_user


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
    Retrieves a user by ID. It utilizes SQLAlchemy's relationships 
    and Pydantic's `from_attributes = True` config to automatically include 
    the nested `TheaterOwner`, `Buyer`, or `Superadmin` data in the response.
    """
    
    db_user = crud_user.get_user(db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    # FastAPI/Pydantic automatically handles the conversion from the SQLAlchemy ORM model 
    # (which contains the nested relationships) to the UserResponse schema.
    return db_user

# NOTE: You would typically include endpoints for login (authentication), 
# reading the current user, updating user details, and deleting a user here.

# Example of a required dependency function (needs to be implemented elsewhere, e.g., in app/core/dependencies.py)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


This `router.py` file provides the structure for your user endpoints. You will need to ensure your main FastAPI application includes this router:

```python
# In your main.py or app/main.py
from fastapi import FastAPI
from app.api.v1.endpoints.router import router as user_router

app = FastAPI()

# Include the user router
app.include_router(user_router, prefix="/v1")