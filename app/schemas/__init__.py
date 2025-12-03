"""
Schemas Module Initialization
=============================

This module serves as the central hub for all Pydantic data models (schemas)
used across the application's API layer and internal logic.

It re-exports models from submodules like ``app.schemas.user``, ``app.schemas.token``,
``app.schemas.role``, and ``app.schemas.booking``, allowing other parts of the
application to import them easily from a single place (e.g., ``from app.schemas import UserResponse``).

The exposed schemas include:

- User-related models for authentication, creation, and profile data.
- JWT models for handling token payloads.
- Role models for access control configuration.
- Booking and Theater models for managing reservations and seat layouts.
"""
# =============================================================================
# Schemas Module Initialization
# =============================================================================

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserInDB,
    UserUpdate,
)
from app.schemas.token import Token, TokenData
from app.schemas.role import RoleBase, RoleCreate, RoleResponse
from app.schemas.booking import (
    SeatBase,
    SeatResponse,
    BookingCreate,
    BookingResponse,
    TheaterResponse,
    BookingStatusResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserInDB",
    "UserUpdate",
    # Token schemas
    "Token",
    "TokenData",
    # Role schemas
    "RoleBase",
    "RoleCreate",
    "RoleResponse",
    # Booking schemas
    "SeatBase",
    "SeatResponse",
    "BookingCreate",
    "BookingResponse",
    "TheaterResponse",
    "BookingStatusResponse",
]