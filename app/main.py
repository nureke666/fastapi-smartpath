# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Создаем таблицы в БД автоматически (для MVP это ок, вместо миграций пока)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartPath API", "status": "running"}