from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials = Depends(security)):
    # Dev mode: fake authenticated user
    user = type('User', (), {})()
    user.id = "dev_user_123"
    user.is_admin = True
    return user

async def get_current_admin(user = Depends(get_current_user)):
    return user