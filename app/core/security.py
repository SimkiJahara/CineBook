# /app/core/security.py (Modified to include get_current_user and dependencies)

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings # Assuming settings holds JWT configuration

# --- Configuration ---
# CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token retrieval from the request header (Bearer Token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")

# --- Utility Functions ---

def get_password_hash(password: str) -> str:
    """Hashes a plaintext password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiry: adjust as needed (e.g., 30 minutes)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "sub": str(data["user_id"])})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# --- Dependency Function (The missing piece) ---

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency that decodes and validates the JWT token, returning the user payload.
    Used to protect endpoints.
    """
    # Define credentials exception for unauthorized access
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        # Extract user ID and ensure it exists
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
        # You could fetch the full user object here if needed, 
        # but returning the payload is often faster for authorization checks.
        return {"id": user_id, "role": payload.get("role")}
        
    except JWTError:
        # Handle decoding errors (e.g., invalid signature, expired token)
        raise credentials_exception

# --- NOTE on settings.py ---
# Ensure your app.core.config.py includes the following variables:
# SECRET_KEY (str)
# ALGORITHM (str, e.g., "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES (int)
# API_V1_STR (str, e.g., "/api/v1")