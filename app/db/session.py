# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Для SQLite нужен специальный аргумент check_same_thread
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=True # Покажет SQL-запросы в консоли (удобно для отладки)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)