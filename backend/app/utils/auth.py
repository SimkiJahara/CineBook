"""
Authentication Utilities
Temporary mock auth for development - integrate with team's auth later
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


class MockUser:
    """Mock user for development"""
    def __init__(self, user_id: int = 1, is_admin: bool = False):
        self.id = user_id
        self.is_admin = is_admin


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> MockUser:
    """
    Get current user from token.
    
    DEV MODE: Returns a mock user for testing.
    PRODUCTION: Replace with actual JWT validation using team's auth.
    """
    # Development mode - return mock user
    # When team's auth is ready, replace this with actual token validation
    return MockUser(user_id=1, is_admin=False)


async def get_current_admin(user: MockUser = Depends(get_current_user)) -> MockUser:
    """
    Verify user is an admin.
    
    DEV MODE: Returns mock admin.
    PRODUCTION: Actually check user's admin status.
    """
    # Development mode - always allow admin actions
    # When ready, check: if not user.is_admin: raise HTTPException(403, "Admin required")
    return MockUser(user_id=1, is_admin=True)


"""
INTEGRATION NOTES:
==================

When your teammate implements the auth module, update this file to:

1. Import their auth service:
   from app.services.auth_service import AuthService

2. Validate JWT tokens:
   async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
       if not credentials:
           raise HTTPException(status_code=401, detail="Not authenticated")
       
       token = credentials.credentials
       user = AuthService.validate_token(token)
       if not user:
           raise HTTPException(status_code=401, detail="Invalid token")
       return user

3. Check admin status from database:
   async def get_current_admin(user = Depends(get_current_user)):
       if user.role != "superadmin":
           raise HTTPException(status_code=403, detail="Admin access required")
       return user
"""