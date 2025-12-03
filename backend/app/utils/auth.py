"""This module is used to test the frontend by creating a mock user"""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


class MockUser:
    """mock user for testing"""
    def __init__(self, user_id=1, is_admin=False):
        self.id = user_id
        self.is_admin = is_admin


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """returns a basic mock user"""
    return MockUser(user_id=1, is_admin=False)
