"""
Pydantic Schemas for JWT Authentication Tokens.

This module defines the data structures used for the JWT payload (TokenData) 
and the API response format returned after a successful login (Token).
"""

from pydantic import BaseModel
from typing import Optional

class TokenData(BaseModel):
    """
    Schema for the data contained within the JWT access token payload.

    This data is decoded from the token to identify and authorize the user.

    :ivar username: The identifier of the user (often the email or user ID).
    :vartype username: Optional[str]
    """
    # This is often the user's ID or username (the subject 'sub' of the JWT)
    username: Optional[str] = None
    # Add fields for role/scope if needed later
    # role: str | None = None

class Token(BaseModel):
    """
    Schema for the response returned to the client upon successful authentication.

    :ivar access_token: The actual JWT string that the client must include in subsequent requests.
    :vartype access_token: str
    :ivar token_type: Indicates the type of token, typically "bearer".
    :vartype token_type: str
    """
    # The actual JWT string
    access_token: str
    # Indicates the type of token (usually "bearer")
    token_type: str = "bearer"