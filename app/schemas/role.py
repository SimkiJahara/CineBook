# =============================================================================
# Role Schemas (Pydantic V2)
# =============================================================================

"""
Role Schemas
============

This module defines the Pydantic data models for handling user roles and
permissions within the application. These schemas ensure consistent validation
for role creation, updates, and retrieval in API interactions.

Key Models:
- **RoleBase**: The fundamental properties required for a role (name and optional description).
- **RoleCreate**: Used for validating incoming data when creating a new role.
- **RoleResponse**: The complete structure of a role returned to the client, including its unique database ID.
"""


from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class RoleBase(BaseModel):
    """Base schema for Role data."""

    name: str = Field(..., min_length=2, max_length=50, description="Role name")
    description: Optional[str] = Field(
        None, max_length=255, description="Role description"
    )


class RoleCreate(RoleBase):
    """Schema for creating a new role."""

    pass


class RoleResponse(RoleBase):
    """Schema for role response data."""

    id: int = Field(..., description="Role's unique identifier")

    model_config = ConfigDict(from_attributes=True)