# app/models/roadmap.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


# 1. Карьера (например, "Python Backend")
class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)

    nodes = relationship("RoadmapNode", back_populates="career")


# 2. Узел роадмапа (например, "Variables", "Loops")
class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"))
    title = Column(String)
    description_content = Column(Text)  # Текст урока или ссылки
    order_index = Column(Integer)  # Порядок: 1, 2, 3...

    career = relationship("Career", back_populates="nodes")
    questions = relationship("Question", back_populates="node")


# 3. Вопросы для проверки (Assessment)
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("roadmap_nodes.id"))
    text = Column(String)
    options_json = Column(String)  # Храним JSON строку: ["A", "B", "C"]
    correct_option_index = Column(Integer)  # Индекс правильного ответа (0, 1 или 2)

    node = relationship("RoadmapNode", back_populates="questions")


# 4. Прогресс пользователя (Самое важное!)
class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    node_id = Column(Integer, ForeignKey("roadmap_nodes.id"))

    # Статус: LOCKED, AVAILABLE, COMPLETED
    status = Column(String, default="LOCKED")

    # Чтобы можно было делать relationship в User
    # user = relationship("User", back_populates="progress")