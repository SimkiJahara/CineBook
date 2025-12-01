# app/utils/auth.py

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


class MockUser:
    """Simple mock user for testing."""

    def __init__(self, user_id=1, is_admin=False):
        self.id = user_id
        self.is_admin = is_admin


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Return a basic mock user.
    """
    return MockUser(user_id=1, is_admin=False)


async def get_current_admin(user=Depends(get_current_user)):
    """
    Return a mock admin user.
    """
    return MockUser(user_id=1, is_admin=True)
