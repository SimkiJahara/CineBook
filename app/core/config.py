"""
Application Configuration Settings.

This module defines the configuration classes and settings used across the
Cinebook API, including project metadata, database connection parameters,
and security constants. Settings are loaded from environment variables
or a .env file using Pydantic's BaseSettings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from pydantic import SecretStr

class UserRole(str, Enum):
    """
    Defines the available user roles in the application.

    Roles are used for authorization and determining user-specific data access.
    """
    buyer = "Buyer"
    theatre_owner = "TheatreOwner"
    super_admin = "Superadmin"

class Settings(BaseSettings): 
    """
    Core application settings loaded from the environment or .env file.

    :ivar PROJECT_NAME: The human-readable name of the project.
    :vartype PROJECT_NAME: str
    :ivar VERSION: The current version string of the API.
    :vartype VERSION: str
    :ivar API_V1_STR: The prefix for the v1 API endpoints.
    :vartype API_V1_STR: str
    :ivar DATABASE_URL: The full connection string for the database (required).
    :vartype DATABASE_URL: str
    :ivar SECRET_KEY: The secret key for cryptographic signing (required).
    :vartype SECRET_KEY: pydantic.SecretStr
    :ivar ALGORITHM: The algorithm used for JWT signing.
    :vartype ALGORITHM: str
    :ivar ACCESS_TOKEN_EXPIRE_MINUTES: Lifetime of the access token in minutes.
    :vartype ACCESS_TOKEN_EXPIRE_MINUTES: int
    :ivar OTP_LENGTH: Length of the One-Time Password code.
    :vartype OTP_LENGTH: int
    :ivar OTP_EXPIRE_MINUTES: Expiry time for the OTP code in minutes.
    :vartype OTP_EXPIRE_MINUTES: int
    """
    
    # Project Configuration
    PROJECT_NAME: str = "Cinebook API"
    VERSION: str = "1.0.0"

    # API Prefix (THE FIX)
    API_V1_STR: str = "/api/v1"

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

