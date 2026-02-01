# app/api/v1/assessment.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.roadmap import Question, UserProgress, RoadmapNode
from app.models.user import User
from app.schemas.quiz import QuestionPublic, AnswerSubmit
from app.api import deps

router = APIRouter()


# 1. Получить вопросы для конкретного урока (Node)
@router.get("/node/{node_id}", response_model=List[QuestionPublic])
def get_quiz_for_node(
        node_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    # Проверим, доступен ли этот урок юзеру? (Нельзя решать тесты закрытых уроков)
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.node_id == node_id
    ).first()

    if not progress or progress.status == "LOCKED":
        raise HTTPException(status_code=403, detail="This lesson is locked.")

    questions = db.query(Question).filter(Question.node_id == node_id).all()

    # Превращаем JSON-строку из БД в Python-список для ответа
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "text": q.text,
            "options": json.loads(q.options_json)  # Распаковка JSON
        })
    return result


# 2. Отправить ответы и (возможно) повысить уровень
@router.post("/node/{node_id}/submit")
def submit_quiz(
        node_id: int,
        answers: List[AnswerSubmit],  # Юзер шлет список ответов
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    # Получаем настоящие вопросы из БД
    questions_db = db.query(Question).filter(Question.node_id == node_id).all()
    if not questions_db:
        raise HTTPException(status_code=404, detail="No quiz found for this node")

    # Считаем правильные ответы
    correct_count = 0
    total_questions = len(questions_db)

    # Создаем словарь правильных ответов {question_id: correct_index}
    correct_map = {q.id: q.correct_option_index for q in questions_db}

    for ans in answers:
        if ans.question_id in correct_map:
            if correct_map[ans.question_id] == ans.selected_option_index:
                correct_count += 1

    # Логика прохождения: нужно 100% правильных (для MVP жестко)
    is_passed = correct_count == total_questions

    if is_passed:
        # 1. Обновляем текущий узел на COMPLETED
        current_progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.node_id == node_id
        ).first()
        current_progress.status = "COMPLETED"

        # 2. Ищем СЛЕДУЮЩИЙ узел и делаем его AVAILABLE
        # Получаем текущую ноду, чтобы узнать её order_index
        current_node = db.query(RoadmapNode).get(node_id)

        # Ищем ноду с order_index + 1
        next_node = db.query(RoadmapNode).filter(
            RoadmapNode.career_id == current_node.career_id,
            RoadmapNode.order_index == current_node.order_index + 1
        ).first()

        if next_node:
            next_progress = db.query(UserProgress).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.node_id == next_node.id
            ).first()
            if next_progress:
                next_progress.status = "AVAILABLE"

        db.commit()
        return {"passed": True, "message": "Great job! Next lesson unlocked."}

    else:
        return {"passed": False, "message": f"You got {correct_count}/{total_questions} correct. Try again!"}