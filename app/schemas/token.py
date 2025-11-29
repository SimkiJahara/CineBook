from pydantic import BaseModel

# Schema for the data contained in the access token (JWT payload)
class TokenData(BaseModel):
    # This is often the user's ID or username (the subject 'sub' of the JWT)
    username: str | None = None
    # Add fields for role/scope if needed later
    # role: str | None = None

# Schema for the response given to the client upon successful login
class Token(BaseModel):
    # The actual JWT string
    access_token: str
    # Indicates the type of token (usually "bearer")
    token_type: str = "bearer"