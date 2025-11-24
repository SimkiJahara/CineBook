from typing import Optional, List, Union, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from app.core.config import UserRole  # Assuming UserRole is an Enum (e.g., in app/core/config.py)
from datetime import datetime

# --- Forward Declarations for Nested Models ---
# Pydantic requires forward references for self-referencing or circularly dependent models.
# The `update_forward_refs()` call at the end handles these.

class TheaterBase(BaseModel):
    """Base schema for the Theater model (used for nesting in TheaterOwner)."""
    companyid: str
    branchid: str
    name: str
    address: str
    
    class Config:
        # Enables conversion from SQLAlchemy model instance to Pydantic object
        from_attributes = True

class TheaterResponse(TheaterBase):
    """Schema for returning Theater data, includes optional fields."""
    contact: Optional[str] = None
    logourl: Optional[str] = None
    isverified: Optional[bool] = None

# --- Specialized Role Schemas (Used for Response Nesting) ---

class TheaterOwnerResponse(BaseModel):
    """Response schema for TheaterOwner, includes the nested Theater list."""
    id: int # Primary key / Foreign key to User.id
    businessname: str
    ownername: str
    phone: Optional[str] = None
    licensenumber: str
    bankdetails: Optional[Dict[str, Any]] = None # Use Dict or Any for JSON field
    logourl: Optional[str] = None
    
    # Nested relationship (One-to-Many: TheaterOwner -> Theaters)
    # The 'theaters' attribute must match the SQLAlchemy model's relationship name.
    theaters: List[TheaterResponse] = [] 

    class Config:
        from_attributes = True

class BuyerResponse(BaseModel):
    """Response schema for the Buyer model."""
    id: int
    fullname: str
    
    class Config:
        from_attributes = True

class SuperadminResponse(BaseModel):
    """Response schema for the Superadmin model."""
    id: int
    
    class Config:
        from_attributes = True


# --- Base User Schemas ---

class UserBase(BaseModel):
    """The common fields for all User types."""
    email: EmailStr
    name: Optional[str] = None
    role: UserRole # Used to determine which specialized schema to return

    # Pydantic's default `Config` is now `model_config` in V2, but `Config` is often used for compatibility.
    class Config:
        from_attributes = True # Important: Allows Pydantic to read ORM objects

class UserInDBBase(UserBase):
    """Common fields for User model stored in the database."""
    id: int
    is_active: bool = True
    # The 'hashed_password' is the key field that distinguishes UserInDB from UserBase/UserResponse
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    
    # We omit the nested role data (theaterowner, buyer, superadmin) 
    # as the DB model itself is often simpler when retrieved for internal use.
    
    class Config:
        from_attributes = True

# The schema used for internal logic (like security checks)
class UserInDB(UserInDBBase):
    """Schema for User model data used internally (e.g., in CRUD and security)."""
    pass 
    # You might include the nested roles here if your ORM populates them 
    # when retrieving the user for authentication, but often they are omitted 
    # to keep the authentication object light.

class UserCreate(UserBase):
    """Schema for creating a new User (Input validation)."""
    
    # 🎯 FIX: Add max_length constraint for the password
    # 72 bytes is the bcrypt limit. Setting a character limit of 70 is safer 
    # and provides a clearer error to the user than server-side truncation.
    password: str = Field(..., min_length=8, max_length=70) 

    # **Specialized Data for Initial Creation**
    # Buyer specific field
    fullname: Optional[str] = None

    # TheaterOwner specific fields
    businessname: Optional[str] = None
    ownername: Optional[str] = None
    phone: Optional[str] = None
    licensenumber: Optional[str] = None
    
    # Validation: Add custom validation logic here (e.g., ensuring required fields are present 
    # based on the `role` value). This is omitted for brevity.


class UserResponse(UserBase):
    """Schema for returning User data (Output structure), including one-to-one nested roles."""
    id: int
    
    # Nested role data. Only one of these will be populated for a given user.
    # The SQLAlchemy ORM will correctly populate the relationship that exists.
    # The response will return 'null' for the roles that don't exist for the user.
    theaterowner: Optional[TheaterOwnerResponse] = None
    buyer: Optional[BuyerResponse] = None
    superadmin: Optional[SuperadminResponse] = None

# Optional: Schema for User update
class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None
    # Add other fields allowed to be updated


    

# --- Update forward references for nested models if using Pydantic V1/complex typing ---
# TheaterOwnerResponse.model_rebuild() # Use for Pydantic V2
# UserResponse.update_forward_refs() # Use for Pydantic V1