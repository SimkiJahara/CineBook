# =============================================================================
# Services Module Initialization
# =============================================================================

from app.services.user_service import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    get_all_users,
    create_user,
    authenticate_user,
    update_user_status,
)
from app.services.role_service import (
    get_role_by_id,
    get_role_by_name,
    get_all_roles,
    create_role,
)
from app.services.booking_service import (
    get_all_seats,
    get_seat_by_id,
    get_theater_layout,
    book_seat,
    cancel_booking,
    get_user_bookings,
    create_seat,
    get_seat_count,
)

__all__ = [
    # User services
    "get_user_by_id",
    "get_user_by_username",
    "get_user_by_email",
    "get_all_users",
    "create_user",
    "authenticate_user",
    "update_user_status",
    # Role services
    "get_role_by_id",
    "get_role_by_name",
    "get_all_roles",
    "create_role",
    # Booking services
    "get_all_seats",
    "get_seat_by_id",
    "get_theater_layout",
    "book_seat",
    "cancel_booking",
    "get_user_bookings",
    "create_seat",
    "get_seat_count",
]
