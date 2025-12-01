"""
Pydantic Schemas for User Management and Role Specialization.

This module defines the data structures used for user creation, database representation, 
and API responses. It implements schema inheritance and uses nested schemas to 
represent the one-to-one and one-to-many relationships defined in the SQLAlchemy models.
"""

from typing import Optional, List, Union, Any, Dict, Literal
from pydantic import BaseModel, EmailStr, Field
from app.core.config import UserRole  # Assuming UserRole is an Enum (e.g., in app/core/config.py)
from datetime import datetime

# --- Forward Declarations for Nested Models ---

class TheaterBase(BaseModel):
    """
    Base schema for the Theatre model (used for nesting in TheatreOwner).

    :ivar companyid: Unique identifier for the theatre company.
    :vartype companyid: str
    :ivar branchid: Unique identifier for the specific branch location.
    :vartype branchid: str
    :ivar name: The name of the theatre branch.
    :vartype name: str
    :ivar address: The physical address of the theatre.
    :vartype address: str
    """
    companyid: str
    branchid: str
    name: str
    address: str
    
    class Config:
        # Enables conversion from SQLAlchemy model instance to Pydantic object
        from_attributes = True

class TheaterResponse(TheaterBase):
    """
    Schema for returning Theater data, includes optional fields.

    :ivar contact: Primary contact number for the theatre.
    :vartype contact: Optional[str]
    :ivar logourl: URL to the theatre's logo image.
    :vartype logourl: Optional[str]
    :ivar isverified: Boolean flag indicating verification status.
    :vartype isverified: Optional[bool]
    """
    contact: Optional[str] = None
    logourl: Optional[str] = None
    isverified: Optional[bool] = None

# --- Specialized Role Schemas (Used for Response Nesting) ---

class TheaterOwnerResponse(BaseModel):
    """
    Response schema for TheaterOwner, includes the nested Theater list.

    :ivar id: Foreign key to User.id.
    :vartype id: int
    :ivar businessname: The registered name of the business.
    :vartype businessname: str
    :ivar ownername: The full name of the owner/contact.
    :vartype ownername: str
    :ivar phone: Contact phone number.
    :vartype phone: Optional[str]
    :ivar licensenumber: Official business license number.
    :vartype licensenumber: str
    :ivar bankdetails: JSON field storing banking or payment processing details.
    :vartype bankdetails: Optional[Dict[str, Any]]
    :ivar logourl: URL to the business logo.
    :vartype logourl: Optional[str]
    :ivar theaters: List of :class:`TheaterResponse` objects managed by this owner.
    :vartype theaters: List[TheaterResponse]
    """
    id: int # Primary key / Foreign key to User.id
    businessname: str
    ownername: str
    phone: Optional[str] = None
    licensenumber: str
    bankdetails: Optional[Dict[str, Any]] = None # Use Dict or Any for JSON field
    logourl: Optional[str] = None
    
    # Nested relationship (One-to-Many: TheaterOwner -> Theaters)
    theaters: List[TheaterResponse] = [] 

    class Config:
        from_attributes = True

class BuyerResponse(BaseModel):
    """
    Response schema for the Buyer model.

    :ivar id: Foreign key to User.id.
    :vartype id: int
    :ivar fullname: The full name of the buyer.
    :vartype fullname: str
    """
    id: int
    fullname: str
    
    class Config:
        from_attributes = True

class SuperadminResponse(BaseModel):
    """
    Response schema for the Superadmin model.

    :ivar id: Foreign key to User.id.
    :vartype id: int
    """
    id: int
    
    class Config:
        from_attributes = True


# --- Base User Schemas ---

class UserBase(BaseModel):
    """
    The common base fields for all User types.

    :ivar email: The unique email address of the user.
    :vartype email: pydantic.EmailStr
    :ivar name: Optional display name.
    :vartype name: Optional[str]
    :ivar role: The user's role, used for authorization.
    :vartype role: app.core.config.UserRole
    """
    email: EmailStr
    name: Optional[str] = None
    role: UserRole 

    class Config:
        from_attributes = True # Important: Allows Pydantic to read ORM objects

class UserInDBBase(UserBase):
    """
    Common fields for User model stored in the database.

    :ivar id: The unique primary key ID.
    :vartype id: int
    :ivar is_active: Activation status (default True).
    :vartype is_active: bool
    :ivar hashed_password: The hashed password string.
    :vartype hashed_password: str
    :ivar created_at: Timestamp of creation.
    :vartype created_at: datetime
    :ivar updated_at: Timestamp of last update.
    :vartype updated_at: datetime
    """
    id: int
    is_active: bool = True
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserInDBBase):
    """
    Schema for User model data used internally (e.g., in CRUD and security).
    """
    pass 

class UserCreate(UserBase):
    """
    The **base** schema for creating a new User (Input validation).
    Includes fields common to all user types plus the password.

    :ivar password: The plaintext password, validated for length before hashing.
    :vartype password: str
    """
    
    # Password field, restricted to ensure bcrypt compatibility
    password: str = Field(..., min_length=8, max_length=70) 


# --- Specialized User Creation Schemas ---

class BuyerCreate(UserCreate):
    """
    Schema for creating a new Buyer user. Inherits base fields from :class:`UserCreate`.

    :ivar fullname: The full name of the buyer (required).
    :vartype fullname: str
    :ivar role: Fixed value enforcing the 'Buyer' role.
    :vartype role: Literal[UserRole.buyer]
    """
    
    # Required field based on the 'buyer' model
    fullname: str

    # FIX: Use Literal to enforce the role value
    role: Literal[UserRole.buyer] = UserRole.buyer


class TheatreOwnerCreate(UserCreate):
    """
    Schema for creating a new TheatreOwner user. Inherits base fields from :class:`UserCreate`.

    :ivar businessname: The registered name of the business.
    :vartype businessname: str
    :ivar ownername: The full name of the owner/contact.
    :vartype ownername: str
    :ivar licensenumber: Mandatory official business license number.
    :vartype licensenumber: str
    :ivar phone: Optional contact phone number.
    :vartype phone: Optional[str]
    :ivar bankdetails: Optional banking details (JSON format).
    :vartype bankdetails: Optional[Dict[str, Any]]
    :ivar logourl: Optional URL to the business logo.
    :vartype logourl: Optional[str]
    :ivar role: Fixed value enforcing the 'TheatreOwner' role.
    :vartype role: Literal[UserRole.theatre_owner]
    """
    
    # Required fields based on the 'theaterowner' model
    businessname: str
    ownername: str
    licensenumber: str
    
    # Optional fields from the model
    phone: Optional[str] = None
    bankdetails: Optional[Dict[str, Any]] = None # For JSON data
    logourl: Optional[str] = None

    # FIX: Use Literal to enforce the role value
    role: Literal[UserRole.theatre_owner] = UserRole.theatre_owner


class SuperadminCreate(UserCreate):
    """
    Schema for creating a new Superadmin user. Inherits base fields from :class:`UserCreate`.
    Used for initial setup.

    :ivar role: Fixed value enforcing the 'Superadmin' role.
    :vartype role: Literal[UserRole.super_admin]
    """
    
    # We only need to enforce the role.
    role: Literal[UserRole.super_admin] = UserRole.super_admin


class UserResponse(UserBase):
    """
    Schema for returning User data (Output structure), including one-to-one nested roles.
    Only one of the nested role fields will be non-null.

    :ivar id: The unique primary key ID.
    :vartype id: int
    :ivar theaterowner: Nested :class:`TheaterOwnerResponse` if the user is a Theatre Owner.
    :vartype theaterowner: Optional[TheaterOwnerResponse]
    :ivar buyer: Nested :class:`BuyerResponse` if the user is a Buyer.
    :vartype buyer: Optional[BuyerResponse]
    :ivar superadmin: Nested :class:`SuperadminResponse` if the user is a Superadmin.
    :vartype superadmin: Optional[SuperadminResponse]
    """
    id: int
    
    # Nested role data. Only one of these will be populated for a given user.
    theaterowner: Optional[TheaterOwnerResponse] = None
    buyer: Optional[BuyerResponse] = None
    superadmin: Optional[SuperadminResponse] = None

# Optional: Schema for User update
class UserUpdate(UserBase):
    """
    Schema for handling user data updates (PATCH requests).
    All fields are optional, allowing partial updates.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None
    # Add other fields allowed to be updated


    

# --- Update forward references for nested models if using Pydantic V1/complex typing ---
# TheaterOwnerResponse.model_rebuild() # Use for Pydantic V2
# UserResponse.update_forward_refs() # Use for Pydantic V1