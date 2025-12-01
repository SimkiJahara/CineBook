# app/settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Load app settings from .env."""
    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
