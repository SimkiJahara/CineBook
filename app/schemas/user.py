# =============================================================================
# User Schemas (Pydantic V2)
# =============================================================================
# Pydantic schemas for request/response validation.
# Refactored to use modern Pydantic V2 syntax with model_config instead of
# the deprecated Config class.
# =============================================================================

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """
    Base schema for User data.

    Contains common fields shared between different user schemas.
    Uses Pydantic V2 syntax for modern type validation.
    """

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(
        None, max_length=100, description="User's full name"
    )


class UserCreate(UserBase):
    """
    Schema for user registration request.

    As described in the article's models.py:
    "class UserCreate(BaseModel):
        username: str
        email: str
        full_name: str
        password: str"

    Refactored to use Pydantic V2 with proper validation.
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)",
    )


class UserResponse(UserBase):
    """
    Schema for user response data.

    Based on the article's User model but enhanced with Pydantic V2 features.
    Does NOT include password or hashed_password for security.
    """

    id: int = Field(..., description="User's unique identifier")
    is_active: bool = Field(default=True, description="Whether user is active")
    roles: List[str] = Field(default_factory=list, description="User's roles")
    created_at: Optional[datetime] = Field(
        None, description="Account creation timestamp"
    )

    # Pydantic V2 configuration using model_config instead of Config class
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """
    Schema representing user data as stored in database.

    As described in the article:
    "class UserInDB(User):
        hashed_password: str"

    This schema includes the hashed password and is used internally only.
    """

    id: int
    hashed_password: str
    is_active: bool = True
    roles: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for updating user data.

    All fields are optional to allow partial updates.
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None
