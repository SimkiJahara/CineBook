from sqlalchemy.orm import Session, joinedload # Import joinedload for clarity
# NOTE: Removed 'db.' prefixes from joinload, use 'joinedload' directly

from app.schemas.user import UserCreate, UserUpdate
from app.core.config import UserRole 
from typing import Optional

# Import the base User model from users.py
from app.models.users import User

# Import the specialized models from their own files
from app.models.buyer import Buyer
from app.models.theatreowner import TheaterOwner
from app.models.superadmin import Superadmin

# --- Helper Function (Password Hashing) ---
# NOTE: In a real app, you'd use a utility for secure hashing (e.g., bcrypt/passlib)
def get_password_hash(password: str) -> str:
    """Placeholder for a real password hashing function."""
    return f"HASHED_{password}"

# --- User CRUD Operations ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a User by their ID, including all nested roles and theaters."""
    # CORRECTION: Added eager loading for all relationships
    return db.query(User).filter(User.id == user_id).options(
        joinedload(User.theaterowner).joinedload(TheaterOwner.theaters), # Nested load for theaters
        joinedload(User.buyer),
        joinedload(User.superadmin),
    ).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a User by their email, including all nested roles and theaters."""
    # CORRECTION: Added nested load for TheaterOwner -> Theaters
    return db.query(User).filter(User.email == email).options(
        # Eagerly load the specific role relationships for the Pydantic response
        joinedload(User.theaterowner).joinedload(TheaterOwner.theaters),
        joinedload(User.buyer),
        joinedload(User.superadmin),
    ).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new User and their corresponding specialized role entry."""
    
    # 1. Prepare User model data
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        name=user_in.name,
        passwordhash=hashed_password,
        role=user_in.role
    )
    
    db.add(db_user)
    db.flush() # Flush to assign 'id' to db_user before committing/creating related models

    # 2. Prepare specialized model data based on role (Same logic as yours)
    if user_in.role == UserRole.buyer:
        db_buyer = Buyer(id=db_user.id, fullname=user_in.fullname)
        db.add(db_buyer)
    elif user_in.role == UserRole.theater_owner:
        db_owner = TheaterOwner(
            id=db_user.id, businessname=user_in.businessname, ownername=user_in.ownername,
            phone=user_in.phone, licensenumber=user_in.licensenumber,
        )
        db.add(db_owner)
    elif user_in.role == UserRole.super_admin:
        db_admin = Superadmin(id=db_user.id)
        db.add(db_admin)

    # 3. Commit the transaction
    db.commit()
    
    # 4. Return the eagerly loaded user object using the corrected get_user function
    return get_user(db, db_user.id) # Use the corrected get_user for a complete response