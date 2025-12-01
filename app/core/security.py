"""
Security Utilities and JWT Authentication.

This module provides functions for password hashing, JWT token creation, and a
FastAPI dependency to authenticate and authorize users based on their access token.
"""

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
    """
    Hashes a plaintext password using the configured CryptContext (bcrypt).

    :param password: The plain text password.
    :type password: str
    :return: The securely hashed password string.
    :rtype: str
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a hashed one.

    :param plain_password: The password provided by the user (unhashed).
    :type plain_password: str
    :param hashed_password: The stored hashed password from the database.
    :type hashed_password: str
    :return: True if the passwords match, False otherwise.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token containing the user's data and an expiry timestamp.

    :param data: The payload data to encode (e.g., {"user_id": 1, "role": "Buyer"}).
    :type data: dict
    :param expires_delta: Optional timedelta for custom token expiration.
    :type expires_delta: Optional[datetime.timedelta]
    :return: The encoded JWT string.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiry: adjust as needed (e.g., 30 minutes)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiry and subject (sub) claims
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

    This function is used to protect API endpoints, ensuring only authenticated users 
    can access them. It validates the token's signature and expiration time.

    :param token: The raw JWT token extracted from the request's Authorization header.
    :type token: str
    :raises HTTPException: 401 Unauthorized if the token is invalid, expired, or missing user data.
    :return: A dictionary containing the authenticated user's ID and role (e.g., {"id": 1, "role": "Buyer"}).
    :rtype: dict
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
            
        # Return a simple user dict for authorization checks
        return {"id": user_id, "role": payload.get("role")}
        
    except JWTError:
        # Handle decoding errors (e.g., invalid signature, expired token)
        raise credentials_exception