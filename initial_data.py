# initial_data.py
import sys
import json

sys.path.append(".")

from app.db.session import SessionLocal, engine
from app.db.base import Base

# --- ВАЖНО: Импортируем ВСЕ модели, чтобы SQLAlchemy знала о них ---
from app.models.user import User  # <--- Этой строки не хватало!
from app.models.roadmap import Career, RoadmapNode, Question, UserProgress


def init_db():
    print("Creating tables...")
    # Создаем таблицы (теперь User импортирован, и ошибка исчезнет)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Проверяем, есть ли данные
    existing_career = db.query(Career).filter(Career.title == "Python Backend Developer").first()
    if existing_career:
        print("Data already exists!")
        db.close()
        return

    print("Creating seed data...")

    # 1. Карьера
    python_career = Career(
        title="Python Backend Developer",
        description="Master Python, APIs, and Databases."
    )
    db.add(python_career)
    db.commit()
    db.refresh(python_career)

    # 2. Узлы и Вопросы
    nodes_data = [
        {
            "title": "Python Basics",
            "desc": "Variables, types.",
            "order": 1,
            "quiz": {
                "text": "Как вывести текст в консоль?",
                "options": ["echo()", "console.log()", "print()"],
                "correct": 2  # print()
            }
        },
        {
            "title": "Control Flow",
            "desc": "Loops and Ifs.",
            "order": 2,
            "quiz": {
                "text": "Какой оператор используется для цикла?",
                "options": ["for", "loop", "repeat"],
                "correct": 0  # for
            }
        },
        # Можешь добавить больше тем по желанию
    ]

    for data in nodes_data:
        # Создаем ноду
        new_node = RoadmapNode(
            career_id=python_career.id,
            title=data["title"],
            description_content=data["desc"],
            order_index=data["order"]
        )
        db.add(new_node)
        db.commit()
        db.refresh(new_node)

        # Создаем вопрос
        if "quiz" in data:
            q_data = data["quiz"]
            new_question = Question(
                node_id=new_node.id,
                text=q_data["text"],
                options_json=json.dumps(q_data["options"]),
                correct_option_index=q_data["correct"]
            )
            db.add(new_question)

    db.commit()
    print("Success! Career, Nodes, and Questions created.")
    db.close()


if __name__ == "__main__":
    init_db()