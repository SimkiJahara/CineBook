from typing import Optional, Type, Any
from sqlalchemy.orm import Session, joinedload

# 1. IMPORT SECURITY FUNCTIONS
from app.core.security import get_password_hash, verify_password

# 2. IMPORT MODELS AND SCHEMAS
from app.schemas.user import UserCreate, UserInDB # Assuming UserInDB is the Pydantic schema for retrieved user data
from app.core.config import UserRole 

# Import the base User model from models/users.py
from app.models.users import User

# Import the specialized models from their own files
from app.models.buyer import Buyer
from app.models.theatreowner import TheatreOwner
from app.models.superadmin import Superadmin


# --- CRUD Class Definition ---

class CRUDUser:
    """
    CRUD operations for the User model, including specialized authentication logic.
    """
    
    # ----------------------------------------------------
    # Public Functions (Existing Logic, updated for class)
    # ----------------------------------------------------

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Retrieve a User by their ID, including all nested roles and theatres."""
        return db.query(User).filter(User.id == user_id).options(
            # FIX: Changed 'theaters' to 'theatres' to match the attribute name in TheatreOwner
            joinedload(User.theaterowner).joinedload(TheatreOwner.theatres),
            joinedload(User.buyer),
            joinedload(User.superadmin),
        ).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Retrieve a User by their email, including all nested roles and theatres."""
        return db.query(User).filter(User.email == email).options(
            # FIX: Changed 'theaters' to 'theatres' to match the attribute name in TheatreOwner
            joinedload(User.theaterowner).joinedload(TheatreOwner.theatres),
            joinedload(User.buyer),
            joinedload(User.superadmin),
        ).first()

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """Create a new User and their corresponding specialized role entry."""
        
        # 1. Prepare User model data (using the real password hash function)
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            name=user_in.name,
            passwordhash=hashed_password, # The column name in your model
            role=user_in.role
        )
        
        db.add(db_user)
        db.flush() 

        # 2. Prepare specialized model data based on role
        if user_in.role == UserRole.buyer:
            # NOTE: Assuming user_in.fullname is passed in the schema for Buyer
            db_buyer = Buyer(id=db_user.id, fullname=user_in.fullname)
            db.add(db_buyer)
        elif user_in.role == UserRole.theater_owner:
            db_owner = TheatreOwner(
                id=db_user.id, businessname=user_in.businessname, ownername=user_in.ownername,
                phone=user_in.phone, licensenumber=user_in.licensenumber,
            )
            db.add(db_owner)
        elif user_in.role == UserRole.super_admin:
            db_admin = Superadmin(id=db_user.id)
            db.add(db_admin)

        # 3. Commit the transaction
        db.commit()
        db.refresh(db_user)
        
        # 4. Return the eagerly loaded user object
        return self.get_user(db, db_user.id)


    # ----------------------------------------------------
    # Authentication Logic (NEW)
    # ----------------------------------------------------

    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Optional[Type[UserInDB]]:
        """
        Retrieves a user by email and verifies the provided plain password.
        """
        # 1. Find the user by email
        user = self.get_user_by_email(db, email=email)
        if not user:
            return None # User not found

        # 2. Verify the password hash stored in the database
        if not verify_password(password, user.passwordhash):
            return None # Password mismatch

        # 3. If authentication is successful, return the user object
        return user


# Create a single instance of the CRUD class to be imported by other modules
crud_user = CRUDUser()