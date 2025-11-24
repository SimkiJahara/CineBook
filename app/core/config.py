from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pydantic import SecretStr #new import for better security

class UserRole(str, Enum):
    buyer = "Buyer"
    theatre_owner = "TheatreOwner"
    super_admin = "Superadmin"

class settings(BaseSettings):

    #database configuration
    # need to learn to use .env files

 #pydantic settings will look for it the .env file
    Database_URL= str


  # Security Configuration (will be used later for JWT)
    # Using SecretStr ensures the value is hidden in logs/dumps for security.
    SECRET_KEY: SecretStr # Changed type, removed hardcoded default
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # OTP Configuration (will be used later)
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    
    # Configuration to load from .env file and ignore extra variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()