"""
core/config.py
--------------
Loads all environment variables using pydantic-settings.
Any setting here can be overridden by creating a .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ResumeIQ"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./resumeiq.db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Resume uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_RESUME_EXTENSIONS: set[str] = {".pdf", ".docx"}

    class Config:
        env_file = ".env"          # reads from .env if it exists
        env_file_encoding = "utf-8"


# Single shared instance — import this everywhere
settings = Settings()
