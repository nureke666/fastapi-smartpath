# app/models/roadmap.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


# Таблица Career теперь хранит всю мета-информацию
class Career(Base):
    __tablename__ = "careers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String)
    description = Column(Text)

    # НОВЫЕ ПОЛЯ META
    difficulty = Column(String)
    total_estimated_hours = Column(Integer)
    total_weeks = Column(Integer)
    focus = Column(String)
    assumptions_json = Column(Text)  # Храним как JSON-строку ["...", "..."]

    modules = relationship("Module", back_populates="career", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="career", cascade="all, delete-orphan")


# RoadmapNode переименовываем в Module для ясности
class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"))
    module_id_str = Column(String)  # "M1", "M2"
    depends_on_json = Column(Text)  # ["M0"]
    topic = Column(String)
    goal = Column(Text)
    summary = Column(Text, nullable=True) # <-- НОВОЕ ПОЛЕ: Краткое содержание
    estimated_hours = Column(Integer)

    # Связи
    career = relationship("Career", back_populates="modules")
    resources = relationship("Resource", back_populates="module", cascade="all, delete-orphan")
    practice_task = relationship("PracticeTask", uselist=False, back_populates="module",
                                 cascade="all, delete-orphan")  # One-to-One
    checkpoint = relationship("Checkpoint", uselist=False, back_populates="module",
                              cascade="all, delete-orphan")  # One-to-One
    questions = relationship("Question", back_populates="module", cascade="all, delete-orphan")


# Новая таблица для Milestones
class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"))
    name = Column(String)
    modules_json = Column(Text)  # ["M1", "M2"]
    outcome = Column(Text)
    career = relationship("Career", back_populates="milestones")


# Улучшаем Resource
class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))  # Связь с Module
    title = Column(String)
    type = Column(String)
    url = Column(String)
    search_query = Column(String, nullable=True) # nullable=True на случай, если AI его не вернет
    level = Column(String)
    why_this = Column(Text)
    time_estimate_hours = Column(Integer)

    module = relationship("Module", back_populates="resources")


# Новые таблицы для Практики и Чекпоинтов
class PracticeTask(Base):
    __tablename__ = "practice_tasks"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), unique=True)
    title = Column(String)
    description = Column(Text)
    deliverables_json = Column(Text)
    acceptance_criteria_json = Column(Text)

    module = relationship("Module", back_populates="practice_task")


class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), unique=True)
    what_to_show = Column(Text)
    how_to_self_check = Column(Text)
    rubric_json = Column(Text, nullable=True) # Храним как JSON-строку

    module = relationship("Module", back_populates="checkpoint")


# Улучшаем Question
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    question_text = Column(Text)
    options_json = Column(Text)
    correct_index = Column(Integer)
    explanation = Column(Text)  # <-- ВАЖНОЕ ПОЛЕ

    module = relationship("Module", back_populates="questions")


# UserProgress теперь ссылается на Module
class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))  # <-- Ссылка на module
    status = Column(String, default="LOCKED")