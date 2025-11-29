from typing import Optional, Type, Any, Union 
from sqlalchemy.orm import Session, joinedload

# 1. IMPORT SECURITY FUNCTIONS
from app.core.security import get_password_hash, verify_password

# 2. IMPORT MODELS AND SCHEMAS
from app.schemas.user import UserCreate, UserInDB, BuyerCreate, TheatreOwnerCreate
# Define the union type for all possible creation schemas
UserCreateUnion = Union[UserCreate, BuyerCreate, TheatreOwnerCreate]
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
    # Public Functions
    # ----------------------------------------------------

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Retrieve a User by their ID, including all nested roles and theatres."""
        return db.query(User).filter(User.id == user_id).options(
            # Correctly eager load the relationships
            joinedload(User.theaterowner).joinedload(TheatreOwner.theatres),
            joinedload(User.buyer),
            joinedload(User.superadmin),
        ).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Retrieve a User by their email, including all nested roles and theatres."""
        return db.query(User).filter(User.email == email).options(
            # Correctly eager load the relationships
            joinedload(User.theaterowner).joinedload(TheatreOwner.theatres),
            joinedload(User.buyer),
            joinedload(User.superadmin),
        ).first()

    def create_user(self, db: Session, user_in: UserCreateUnion) -> User:
        """Create a new User and their corresponding specialized role entry."""
        
        # 1. Prepare User model data
        hashed_password = get_password_hash(user_in.password)
        
        # --- FIX: Determine the 'name' field for the base User model ---
        # 1. Start with the default 'name' from the base UserCreate schema (or None)
        user_display_name = getattr(user_in, 'name', None)

        # 2. Override/set the name using role-specific fields if available
        if hasattr(user_in, 'fullname') and user_in.role == UserRole.buyer:
            user_display_name = user_in.fullname
        elif hasattr(user_in, 'ownername') and user_in.role == UserRole.theatre_owner:
            user_display_name = user_in.ownername

        # Create the base User entry
        db_user = User(
            email=user_in.email,
            name=user_display_name, 
            passwordhash=hashed_password, 
            role=user_in.role
        )
        
        db.add(db_user)
        db.flush() # Flush to get the db_user.id for the foreign key

        # 2. Prepare specialized model data based on role
        if user_in.role == UserRole.buyer:
            # Safely access the 'fullname' field which exists on BuyerCreate
            db_buyer = Buyer(id=db_user.id, fullname=user_in.fullname)
            db.add(db_buyer)
        elif user_in.role == UserRole.theatre_owner:
            # Safely map all required fields from TheatreOwnerCreate
            db_owner = TheatreOwner(
                id=db_user.id, 
                businessname=user_in.businessname, 
                ownername=user_in.ownername,
                licensenumber=user_in.licensenumber,
                # Optional fields are safely retrieved, defaulting to None if missing in the payload
                phone=getattr(user_in, 'phone', None), 
                bankdetails=getattr(user_in, 'bankdetails', None), 
                logourl=getattr(user_in, 'logourl', None),
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
    # Authentication Logic 
    # ----------------------------------------------------

    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Retrieves a user by email and verifies the provided plain password.
        """
        # 1. Find the user by email (eagerly loads nested roles)
        user = self.get_user_by_email(db, email=email)
        if not user:
            return None # User not found

        # 2. Verify the password hash stored in the database
        if not verify_password(password, user.passwordhash):
            return None # Password mismatch

        # 3. If authentication is successful, return the user object
        # NOTE: Returning the ORM object which matches the UserInDBBase data structure
        return user


# Create a single instance of the CRUD class to be imported by other modules
crud_user = CRUDUser()