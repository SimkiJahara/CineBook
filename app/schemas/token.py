# =============================================================================
# Token Schemas (Pydantic V2)
# =============================================================================

"""
Token Schemas
=============

This module defines the Pydantic data models for handling JSON Web Tokens (JWT)
used for authentication and authorization within the API.

These schemas facilitate the validation of token issuance and the extraction
of essential data from the token payload.

Key Models:
- **Token**: Used to structure the API response when a new access token is issued.
- **TokenData**: Represents the decoded claims extracted from the JWT, typically containing
  the user identity (username).
"""



from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Schema for token response.

    As described in the article's login endpoint:
    "return {"access_token": access_token, "token_type": "bearer"}"
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """
    Schema for decoded token data.

    Contains the claims extracted from a JWT token.

    The 'sub' claim contains the username as described in the article:
    "data={"sub": user.username}"
    """

    username: Optional[str] = Field(
        None, description="Username from token subject claim"
    )