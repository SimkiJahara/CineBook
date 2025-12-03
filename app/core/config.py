# =============================================================================
# Application Configuration Module
# =============================================================================
# Refactored for security: Using pydantic-settings to load all configuration
# from environment variables instead of hardcoding secrets in code.
# This follows the 12-factor app methodology for configuration management.
# =============================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class uses pydantic-settings to automatically load configuration
    from .env files and environment variables, ensuring secrets are never
    hardcoded in the source code.

    :ivar app_name: The name of the application displayed in API docs.
    :vartype app_name: str
    :ivar app_version: The version of the application.
    :vartype app_version: str
    :ivar debug: Enable debug mode for development.
    :vartype debug: bool
    :ivar database_url: PostgreSQL connection string. (Required from environment)
    :vartype database_url: str
    :ivar secret_key: Secret key for JWT token signing (CRITICAL - keep secure). (Required from environment)
    :vartype secret_key: str
    :ivar algorithm: Algorithm used for JWT encoding.
    :vartype algorithm: str
    :ivar access_token_expire_minutes: Token expiration time in minutes.
    :vartype access_token_expire_minutes: int
    """

    # Application Settings
    app_name: str = "FastAPI Authentication Demo"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database Configuration
    # Refactored for security: Database URL loaded from environment variable
    # instead of hardcoded SQLite path as in the original article
    database_url: str

    # JWT Configuration
    # Refactored for security: Secret key MUST be loaded from environment
    # The original article had: SECRET_KEY = "your-secret-key-here" (INSECURE)
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Pydantic V2 configuration using model_config instead of Config class
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance.

    :returns: The application configuration object.
    :rtype: Settings
    """
    return Settings()