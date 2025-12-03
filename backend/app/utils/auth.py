"""Authentication utilities module for CineBook API.

Provides mock authentication for development.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer(auto_error=False)


class MockUser:
    """Mock user class for development."""

    def __init__(self, user_id: int = 1, is_admin: bool = False):
        """Initialize mock user.

        :param user_id: User identifier.
        :param is_admin: Admin status.
        """
        self.id = user_id
        self.is_admin = is_admin


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> MockUser:
    """Get current user (mock for development).

    :param credentials: HTTP authorization credentials.
    :return: MockUser instance.
    """
    # Development mode - return mock user
    # When team's auth is ready, replace this with actual token validation
    return MockUser(user_id=1, is_admin=False)


async def get_current_admin(user: MockUser = Depends(get_current_user)) -> MockUser:
    """Get current admin user (mock for development).

    :param user: Current user.
    :return: MockUser instance with admin privileges.
    """
    # Development mode - always allow admin actions
    # When ready, check: if not user.is_admin: raise HTTPException(403, "Admin required")
    return MockUser(user_id=1, is_admin=True)
