# app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Импортируем модели сюда, чтобы Alembic их видел
# (Порядок важен: сначала Base, потом модели)
from app.models.user import User
from app.models.roadmap import Career, RoadmapNode, Question, UserProgress