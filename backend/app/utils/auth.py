
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


class MockUser:
    """Mock user for development"""
    def __init__(self, user_id: int = 1, is_admin: bool = False):
        self.id = user_id
        self.is_admin = is_admin


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> MockUser:
   
    # Development mode - return mock user
    # When team's auth is ready, replace this with actual token validation
    return MockUser(user_id=1, is_admin=False)


async def get_current_admin(user: MockUser = Depends(get_current_user)) -> MockUser:
   
    # Development mode - always allow admin actions
    # When ready, check: if not user.is_admin: raise HTTPException(403, "Admin required")
    return MockUser(user_id=1, is_admin=True)


