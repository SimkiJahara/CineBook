# =============================================================================
# Security Utilities Module
# =============================================================================
# This module contains all security-related functionality including password


from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


# Password hashing context using bcrypt
# The CryptContext handles password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""
:class:`passlib.context.CryptContext` instance configured for bcrypt hashing.
"""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    
    This prevents timing attacks by using constant-time comparison.

    :param plain_password: The plain text password to verify.
    :type plain_password: str
    :param hashed_password: The bcrypt hashed password to compare against.
    :type hashed_password: str
    :returns: True if password matches, False otherwise.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash for a password.

  "Production apps should never store passwords
    in plain text. Instead, you need to hash passwords using secure algorithms."

    :param password: The plain text password to hash.
    :type password: str
    :returns: The bcrypt hashed password.
    :rtype: str
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    "JSON Web Tokens (JWT) provide a secure way
    to authenticate users without storing sessions on the server. Each token
    contains all the user information needed, making your API stateless and scalable."

    Refactored for security: SECRET_KEY is loaded from environment variables
    instead of being hardcoded.

    :param data: Dictionary of claims to encode in the token.
    :type data: dict
    :param expires_delta: Optional custom expiration time.
    :type expires_delta: :class:`datetime.timedelta`, optional
    :returns: The encoded JWT token.
    :rtype: str
    """
    settings = get_settings()
    to_encode = data.copy()

    # Use timezone-aware UTC timestamps as recommended in the article
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Extracts the payload from the JWT token after verifying its signature.

    :param token: The JWT token string to decode.
    :type token: str
    :returns: The decoded token payload if valid, None if invalid due to signature or expiration.
    :rtype: dict | None
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None