# app/api/v1/roadmap.py
import json
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.db.session import SessionLocal
from app.models.roadmap import Career, UserProgress, Module, Question, Resource
from app.models.user import User
from app.schemas.roadmap import CareerResponse, RoadmapGenerateRequest
from app.services.ai_roadmap import ai_service
from app.api import deps

router = APIRouter()


def _module_order_key(module: Module) -> int:
    if module.module_id_str:
        match = re.search(r"\d+", module.module_id_str)
        if match:
            return int(match.group())
    return module.id or 0


def _career_to_response(career: Career, progress_map: dict[int, str] | None = None) -> dict:
    modules = sorted(career.modules or [], key=_module_order_key)
    progress_map = progress_map or {}

    nodes = []
    for module in modules:
        nodes.append({
            "id": module.id,
            "title": module.topic or (module.module_id_str or ""),
            "description_content": module.goal,
            "order_index": _module_order_key(module),
            "status": progress_map.get(module.id, "LOCKED"),
            "resources": module.resources or [],
        })

    return {
        "id": career.id,
        "title": career.title,
        "description": career.description,
        "nodes": nodes,
    }


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

    user_progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()
    progress_map = {p.module_id: p.status for p in user_progress_records}

    return [_career_to_response(career, progress_map) for career in careers]


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
    modules = sorted(career.modules or [], key=_module_order_key)
    if not modules:
        raise HTTPException(status_code=400, detail="Career has no modules")

    existing_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.module_id == modules[0].id  # Проверяем по первому модулю
    ).first()

    if existing_progress:
        return {"message": "Career already started"}

    # 3. Создаем записи прогресса для ВСЕХ узлов этой карьеры
    progress_list = []
    for idx, module in enumerate(modules):
        # Первый модуль -> AVAILABLE, остальные -> LOCKED
        initial_status = "AVAILABLE" if idx == 0 else "LOCKED"

        new_progress = UserProgress(
            user_id=current_user.id,
            module_id=module.id,
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

    progress_map = {p.module_id: p.status for p in user_progress_records}

    return _career_to_response(career, progress_map)


@router.post("/generate", response_model=CareerResponse, deprecated=True)
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
        module_id_str = f"M{idx + 1}"
        depends_on = [f"M{idx}"] if idx > 0 else []
        new_module = Module(
            career_id=new_career.id,
            module_id_str=module_id_str,
            depends_on_json=json.dumps(depends_on),
            topic=node_data.get("title"),
            goal=node_data.get("desc"),
            estimated_hours=node_data.get("estimated_hours", 0)
        )
        db.add(new_module)
        db.commit()
        db.refresh(new_module)

        if "resources" in node_data:
            for res in node_data["resources"]:
                new_res = Resource(
                    module_id=new_module.id,
                    title=res["title"],
                    type=res["type"],
                    url=res["url"],
                    level=res.get("level", "beginner"),
                    why_this=res.get("why_this", ""),
                    time_estimate_hours=res.get("time_estimate_hours", 0)
                )
                db.add(new_res)

        # Сохраняем тест
        if "quiz" in node_data and isinstance(node_data["quiz"], list):
            for q in node_data["quiz"]:
                new_question = Question(
                    module_id=new_module.id,
                    question_text=q["text"],
                    options_json=json.dumps(q["options"]),
                    correct_index=q["correct"],
                    explanation=q.get("explanation", "")
                )
                db.add(new_question)

        db.commit()


    db.refresh(new_career)
    return _career_to_response(new_career, {})
