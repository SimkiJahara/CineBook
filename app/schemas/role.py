# =============================================================================
# Role Schemas (Pydantic V2)
# =============================================================================
# Schemas for role request and response validation.
# =============================================================================

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
