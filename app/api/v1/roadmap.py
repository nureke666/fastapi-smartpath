# app/api/v1/roadmap.py
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.db.session import SessionLocal
from app.models.roadmap import Career, UserProgress, RoadmapNode, Question
from app.models.user import User
from app.schemas.roadmap import CareerResponse, RoadmapGenerateRequest
from app.services.ai_roadmap import ai_service
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[CareerResponse])
def get_all_careers(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)  # Теперь нужен токен!
):
    """
    Показывает:
    1. Общие шаблоны (user_id IS NULL)
    2. Личные роадмапы этого пользователя (user_id == current_user.id)
    """
    careers = db.query(Career).filter(
        or_(
            Career.user_id == None,  # Общие
            Career.user_id == current_user.id  # Личные
        )
    ).all()

    return careers


@router.post("/{career_id}/start", status_code=201)
def start_career(
        career_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    """
    Начать обучение: создает записи прогресса для юзера.
    Первый узел становится AVAILABLE, остальные LOCKED.
    """
    # 1. Проверяем, существует ли карьера
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    # 2. Проверяем, не начал ли он уже (чтобы не сбросить прогресс)
    existing_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.node_id == career.nodes[0].id  # Проверяем по первому узлу
    ).first()

    if existing_progress:
        return {"message": "Career already started"}

    # 3. Создаем записи прогресса для ВСЕХ узлов этой карьеры
    progress_list = []
    for node in career.nodes:
        # Если это первый шаг (order_index == 1) -> AVAILABLE, иначе LOCKED
        initial_status = "AVAILABLE" if node.order_index == 1 else "LOCKED"

        new_progress = UserProgress(
            user_id=current_user.id,
            node_id=node.id,
            status=initial_status
        )
        db.add(new_progress)

    db.commit()
    return {"message": "Career started successfully"}


@router.get("/{career_id}", response_model=CareerResponse)
def get_career_details(
        career_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    """
    Получить роадмап с ПЕРСОНАЛЬНЫМИ статусами (Locked/Available/Completed).
    """
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    # 1. Получаем прогресс юзера из БД
    # Делаем словарь: {node_id: "STATUS"} для быстрого поиска
    user_progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()

    progress_map = {p.node_id: p.status for p in user_progress_records}

    # 2. Собираем ответ, подставляя статусы
    # Pydantic сам соберет структуру, нам нужно только модифицировать объекты перед отдачей
    # Но так как SQLAlchemy объекты привязаны к сессии, мы не можем их менять напрямую.
    # Поэтому Pydantic сделает это за нас, если мы правильно передадим данные.

    # Трюк: мы временно "приклеиваем" статус к объектам нод, чтобы Pydantic их увидел
    for node in career.nodes:
        # Если запись есть в прогрессе - берем оттуда, если нет - LOCKED
        node.status = progress_map.get(node.id, "LOCKED")

    return career


@router.post("/generate", response_model=CareerResponse)
def generate_custom_roadmap(
        request: RoadmapGenerateRequest,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    """
    Принимает анкету, генерирует роадмап через AI (или Mock),
    сохраняет его в БД как личный роадмап юзера.
    """
    # 1. Вызываем AI
    ai_data = ai_service.generate_roadmap(
        role=request.target_role,
        experience=request.current_experience,
        goal=request.goal,
        hours=request.hours_per_week
    )

    # 2. Создаем новую карьеру в БД (привязанную к user_id)
    new_career = Career(
        user_id=current_user.id,  # ПРИВЯЗКА К ЮЗЕРУ!
        title=ai_data["title"],
        description=ai_data["description"]
    )
    db.add(new_career)
    db.commit()
    db.refresh(new_career)

    # 3. Сохраняем узлы и тесты
    for idx, node_data in enumerate(ai_data["nodes"]):
        new_node = RoadmapNode(
            career_id=new_career.id,
            title=node_data["title"],
            description_content=node_data["desc"],
            order_index=idx + 1
        )
        db.add(new_node)
        db.commit()
        db.refresh(new_node)

        # Сохраняем тест
        if "quiz" in node_data:
            q = node_data["quiz"]
            new_question = Question(
                node_id=new_node.id,
                text=q["text"],
                options_json=json.dumps(q["options"]),
                correct_option_index=q["correct"]
            )
            db.add(new_question)

    db.commit()

    # 4. Сразу подготавливаем ответ с пустыми статусами
    # (Pydantic схема CareerResponse ожидает status у нод, добавим их вручную)
    for node in new_career.nodes:
        node.status = "LOCKED"

    return new_career