"""
CRUD operations for the User model.

This module provides the CRUD (Create, Retrieve, Update, Delete) interface for
the application's User model, handling complex operations such as:
1. Eagerly loading nested role data (Buyer, TheatreOwner, Superadmin) during retrieval.
2. Hashing passwords and creating specialized role records during user creation.
3. Authenticating users against stored password hashes.
"""

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
        """
        Retrieve a User by their ID, including all nested roles and theatres.

        Uses :func:`~sqlalchemy.orm.joinedload` to eagerly fetch related Buyer, 
        TheatreOwner, and Superadmin records, as well as the associated Theatres 
        for the TheatreOwner.

        :param db: The database session.
        :type db: sqlalchemy.orm.Session
        :param user_id: The unique integer ID of the user.
        :type user_id: int
        :return: The fully loaded :class:`~app.models.users.User` object or None.
        :rtype: Optional[app.models.users.User]
        """
        return db.query(User).filter(User.id == user_id).options(
            # Correctly eager load the relationships
            joinedload(User.theaterowner).joinedload(TheatreOwner.theatres),
            joinedload(User.buyer),
            joinedload(User.superadmin),
        ).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Retrieve a User by their email, including all nested roles and theatres.

        Uses :func:`~sqlalchemy.orm.joinedload` to eagerly fetch related role data.

        :param db: The database session.
        :type db: sqlalchemy.orm.Session
        :param email: The email address of the user.
        :type email: str
        :return: The fully loaded :class:`~app.models.users.User` object or None.
        :rtype: Optional[app.models.users.User]
        """
        return db.query(User).filter(User.email == email).options(
            # Correctly eager load the relationships
            joinedload(User.theaterowner).joinedload(TheatreOwner.theatres),
            joinedload(User.buyer),
            joinedload(User.superadmin),
        ).first()

    def create_user(self, db: Session, user_in: UserCreateUnion) -> User:
        """
        Create a new User and their corresponding specialized role entry.

        This function handles password hashing, sets the appropriate display name,
        and creates the corresponding record in the Buyer, TheatreOwner, or 
        Superadmin table based on the role specified in the input schema.

        :param db: The database session.
        :type db: sqlalchemy.orm.Session
        :param user_in: The Pydantic schema containing user details, specialized by role.
        :type user_in: UserCreateUnion
        :return: The newly created and eagerly loaded :class:`~app.models.users.User` object.
        :rtype: app.models.users.User
        """
        
        # 1. Prepare User model data
        hashed_password = get_password_hash(user_in.password)
        
        # --- Determine the 'name' field for the base User model ---
        user_display_name = getattr(user_in, 'name', None)

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
            db_buyer = Buyer(id=db_user.id, fullname=user_in.fullname)
            db.add(db_buyer)
        elif user_in.role == UserRole.theatre_owner:
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

        :param db: The database session.
        :type db: sqlalchemy.orm.Session
        :param email: The email address to check.
        :type email: str
        :param password: The plain text password to verify.
        :type password: str
        :return: The authenticated :class:`~app.models.users.User` object, or None if authentication fails.
        :rtype: Optional[app.models.users.User]
        """
        # 1. Find the user by email (eagerly loads nested roles)
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