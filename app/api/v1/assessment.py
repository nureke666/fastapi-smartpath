# app/api/v1/assessment.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.roadmap import Question, UserProgress, Module
from app.models.user import User
from app.schemas.quiz import QuestionPublic, AnswerSubmit
from app.api import deps

router = APIRouter()


# 1. Получить вопросы для конкретного урока (Module)
@router.get("/node/{module_id}", response_model=List[QuestionPublic])
def get_quiz_for_node(
        module_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    # Проверим, доступен ли этот урок юзеру? (Нельзя решать тесты закрытых уроков)
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.module_id == module_id
    ).first()

    if not progress or progress.status == "LOCKED":
        raise HTTPException(status_code=403, detail="This lesson is locked.")

    questions = db.query(Question).filter(Question.module_id == module_id).all()

    # Превращаем JSON-строку из БД в Python-список для ответа
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "text": q.question_text,  # В модели Question поле называется question_text
            "options": json.loads(q.options_json)  # Распаковка JSON
        })
    return result


# 2. Отправить ответы и (возможно) повысить уровень
@router.post("/node/{module_id}/submit")
def submit_quiz(
        module_id: int,
        answers: List[AnswerSubmit],  # Юзер шлет список ответов
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    # Получаем настоящие вопросы из БД
    questions_db = db.query(Question).filter(Question.module_id == module_id).all()
    if not questions_db:
        raise HTTPException(status_code=404, detail="No quiz found for this module")

    # Считаем правильные ответы
    correct_count = 0
    total_questions = len(questions_db)

    # Создаем словарь правильных ответов {question_id: correct_index}
    # В модели Question поле называется correct_index
    correct_map = {q.id: q.correct_index for q in questions_db}

    for ans in answers:
        if ans.question_id in correct_map:
            if correct_map[ans.question_id] == ans.selected_option_index:
                correct_count += 1

    # Логика прохождения: нужно 70% правильных
    score_percent = (correct_count / total_questions) * 100
    is_passed = score_percent >= 70

    if is_passed:
        # 1. Обновляем текущий узел на COMPLETED
        current_progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.module_id == module_id
        ).first()
        if current_progress:
            current_progress.status = "COMPLETED"

        # 2. Ищем СЛЕДУЮЩИЙ узел и делаем его AVAILABLE
        # Получаем текущий модуль
        current_module = db.query(Module).get(module_id)
        
        all_modules = db.query(Module).filter(Module.career_id == current_module.career_id).all()
        # Сортируем по ID (предполагаем, что они создавались по порядку)
        all_modules.sort(key=lambda x: x.id)
        
        try:
            curr_idx = next(i for i, m in enumerate(all_modules) if m.id == module_id)
            if curr_idx + 1 < len(all_modules):
                next_module = all_modules[curr_idx + 1]
                
                next_progress = db.query(UserProgress).filter(
                    UserProgress.user_id == current_user.id,
                    UserProgress.module_id == next_module.id
                ).first()
                
                if next_progress:
                    next_progress.status = "AVAILABLE"
        except StopIteration:
            pass

        db.commit()
        
        msg = "Great job! Next lesson unlocked."
        if score_percent == 100:
            msg = "Perfect score! You are a master!"
            
        return {"passed": True, "message": msg}

    else:
        return {"passed": False, "message": f"You got {correct_count}/{total_questions} correct ({int(score_percent)}%). Need 70% to pass."}
