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
