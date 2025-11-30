# /app/core/config.py (Modified)

from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pydantic import SecretStr

class UserRole(str, Enum):
    buyer = "Buyer"
    theatre_owner = "TheatreOwner"
    super_admin = "Superadmin"

class Settings(BaseSettings): 
    
    # Project Configuration
    PROJECT_NAME: str = "Cinebook API"
    VERSION: str = "1.0.0"

    # API Prefix (THE FIX)
    API_V1_STR: str = "/api/v1"  # <--- NEW: This line resolves the AttributeError

    # Database Configuration
    DATABASE_URL: str 

    # Security Configuration
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # OTP Configuration
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    
    # Configuration to load from .env file and ignore extra variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Instantiate the settings object
settings = Settings()