# app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartPath MVP"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./smartpath.db"

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    class Config:
        case_sensitive = True


settings = Settings()