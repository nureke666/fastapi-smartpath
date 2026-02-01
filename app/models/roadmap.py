# app/models/roadmap.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


# 1. Карьера (например, "Python Backend")
class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, index=True)
    description = Column(String)

    nodes = relationship("RoadmapNode", back_populates="career", cascade="all, delete-orphan")


class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"))
    title = Column(String)
    description_content = Column(Text)
    order_index = Column(Integer)

    career = relationship("Career", back_populates="nodes")
    questions = relationship("Question", back_populates="node", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("roadmap_nodes.id"))
    text = Column(String)
    options_json = Column(String)
    correct_option_index = Column(Integer)
    node = relationship("RoadmapNode", back_populates="questions")


class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    node_id = Column(Integer, ForeignKey("roadmap_nodes.id"))
    status = Column(String, default="LOCKED")