from sqlalchemy.orm import Session
from app.models.user import User, TheaterOwner, Buyer, Superadmin # Import your SQLAlchemy models
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import UserRole # Import the UserRole enum
from typing import Optional

# --- Helper Function (Password Hashing) ---
# NOTE: In a real app, you'd use a utility for secure hashing (e.g., bcrypt/passlib)
def get_password_hash(password: str) -> str:
    """Placeholder for a real password hashing function."""
    # TODO: Implement secure hashing (e.g., return pwd_context.hash(password))
    return f"HASHED_{password}"

# --- User CRUD Operations ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a User by their ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a User by their email, used for login."""
    # Use joinload to eagerly load the one-to-one relationships for efficient response mapping
    return db.query(User).filter(User.email == email).options(
        # Eagerly load the specific role relationships for the Pydantic response
        db.joinedload(User.theaterowner),
        db.joinedload(User.buyer),
        db.joinedload(User.superadmin),
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

    # 2. Prepare specialized model data based on role
    if user_in.role == UserRole.buyer:
        # Create a Buyer entry linked to the new User's ID
        db_buyer = Buyer(
            id=db_user.id, # Link using the FK/PK
            fullname=user_in.fullname # Get data from the create schema
        )
        db.add(db_buyer)

    elif user_in.role == UserRole.theater_owner:
        # Create a TheaterOwner entry
        db_owner = TheaterOwner(
            id=db_user.id,
            businessname=user_in.businessname,
            ownername=user_in.ownername,
            phone=user_in.phone,
            licensenumber=user_in.licensenumber,
            # bankdetails and logourl can be set to None/default if not provided
        )
        db.add(db_owner)

    elif user_in.role == UserRole.super_admin:
        # Create a Superadmin entry (minimal data)
        db_admin = Superadmin(id=db_user.id)
        db.add(db_admin)

    # 3. Commit the transaction
    db.commit()
    db.refresh(db_user) # Refresh to get all relationships populated
    
    # Eagerly load for the final return to ensure the nested data is available
    return get_user_by_email(db, db_user.email)