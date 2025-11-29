from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pydantic import SecretStr

class UserRole(str, Enum):
    buyer = "Buyer"
    theatre_owner = "TheatreOwner"
    super_admin = "Superadmin"

class Settings(BaseSettings): # Note: Changed class name to Settings (capital S) for convention
    

    # Project Configuration (New additions)
    PROJECT_NAME: str = "Cinebook API" # <-- Add this
    VERSION: str = "1.0.0"

    # database configuration
    # **FIX 1: Change to all-caps for consistency and to match app/core/db.py**
    DATABASE_URL: str 

    # Security Configuration (will be used later for JWT)
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # OTP Configuration (will be used later)
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    
    # Configuration to load from .env file and ignore extra variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Note: Renaming the class to Settings requires this instance name change too
settings = Settings()