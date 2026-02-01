# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartPath MVP"
    API_V1_STR: str = "/api/v1"

    # Используем SQLite для MVP (файл будет создан в корне проекта)
    DATABASE_URL: str = "sqlite:///./smartpath.db"

    class Config:
        case_sensitive = True


settings = Settings()