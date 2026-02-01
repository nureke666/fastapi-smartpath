# initial_data.py
import sys

# Добавляем текущую директорию в путь, чтобы видеть app
sys.path.append(".")

from app.db.session import SessionLocal, engine
from app.models.roadmap import Career, RoadmapNode, Question
from app.db.base import Base


def init_db():
    db = SessionLocal()

    # 1. Проверяем, есть ли уже данные, чтобы не дублировать
    existing_career = db.query(Career).filter(Career.title == "Python Backend Developer").first()
    if existing_career:
        print("Data already exists!")
        return

    print("Creating seed data...")

    # 2. Создаем Карьеру
    python_career = Career(
        title="Python Backend Developer",
        description="Master Python, APIs, and Databases to become a backend engineer."
    )
    db.add(python_career)
    db.commit()
    db.refresh(python_career)

    # 3. Создаем Узлы (Roadmap Nodes)
    nodes_data = [
        {
            "title": "Python Basics",
            "desc": "Variables, Data Types, Lists, Dictionaries. The foundation of code.",
            "order": 1
        },
        {
            "title": "Control Flow & Loops",
            "desc": "If/Else statements, For and While loops. Logic control.",
            "order": 2
        },
        {
            "title": "Functions & Modules",
            "desc": "Writing reusable code, importing libraries, understanding scope.",
            "order": 3
        },
        {
            "title": "Object-Oriented Programming (OOP)",
            "desc": "Classes, Objects, Inheritance, Polymorphism.",
            "order": 4
        },
        {
            "title": "FastAPI & Web Basics",
            "desc": "HTTP methods, Routing, Pydantic schemas. Your first API.",
            "order": 5
        }
    ]

    for node in nodes_data:
        new_node = RoadmapNode(
            career_id=python_career.id,
            title=node["title"],
            description_content=node["desc"],
            order_index=node["order"]
        )
        db.add(new_node)

    db.commit()
    print("Success! Career and Nodes created.")
    db.close()


if __name__ == "__main__":
    # Создаем таблицы на всякий случай
    Base.metadata.create_all(bind=engine)
    init_db()