# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.v1 import auth, roadmap, assessment, roadmap_v2

# Создаем таблицы в БД автоматически (для MVP это ок, вместо миграций пока)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <--- Звездочка разрешает доступ с любого сайта/порта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roadmap.router, prefix="/api/v1/roadmaps", tags=["roadmaps"])
app.include_router(assessment.router, prefix="/api/v1/quiz", tags=["quiz"])
app.include_router(roadmap_v2.router, prefix="/api/v2/roadmaps", tags=["Roadmaps (v2)"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartPath API", "status": "running"}