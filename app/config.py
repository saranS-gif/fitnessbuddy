import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FitBuddy"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    SECRET_KEY: str = "fitbuddy-super-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///./fitbuddy.db"

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def model_post_init(self, __context: object) -> None:
        # On Vercel serverless functions, the root filesystem is read-only.
        # Use /tmp for SQLite database storage if running on Vercel.
        if os.environ.get("VERCEL") and self.DATABASE_URL.startswith("sqlite:///."):
            self.DATABASE_URL = "sqlite:////tmp/fitbuddy.db"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
