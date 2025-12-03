# =============================================================================
# Models Module Initialization
# =============================================================================
"""
Public interface for the application's database models.

This module re-exports all essential SQLAlchemy models and related components,
making them easily accessible from the top level of the ``app.models`` package.
"""

from app.models.user import User, user_roles
from app.models.role import Role
from app.models.booking import Seat, Booking, SeatType

#: Application User model, representing a user account.
User = User
#: SQLAlchemy Table object defining the many-to-many relationship between User and Role.
user_roles = user_roles
#: Application Role model, defining user permissions.
Role = Role
#: Seat model, representing a physical seat or resource.
Seat = Seat
#: Booking model, representing a user's reservation of a Seat.
Booking = Booking
#: Enum for different types of seats (e.g., standard, VIP).
SeatType = SeatType

__all__ = [
    "User",
    "Role",
    "user_roles",
    "Seat",
    "Booking",
    "SeatType",
]