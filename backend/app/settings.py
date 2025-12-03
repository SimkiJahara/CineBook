from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Loads app settings from .env"""
    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
