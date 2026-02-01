# app/api/v1/roadmap_v2.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Импортируем все наши новые модели
from app.models.user import User
from app.models.roadmap import (
    Career, Module, Milestone, Resource, PracticeTask, Checkpoint, Question
)
# Импортируем новые схемы
from app.schemas.roadmap_v2 import (
    RoadmapGenerateRequestV2, CareerResponseV2, RoadmapMetaResponse,
    ModuleResponse, MilestoneResponse
)
from app.api import deps
from app.services.ai_roadmap_v2 import ai_service  # Мы создадим этот сервис в след. шаге

router = APIRouter()


@router.post("/generate", response_model=CareerResponseV2)
def generate_custom_roadmap_v2(
        request: RoadmapGenerateRequestV2,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user)
):
    try:
        ai_data = ai_service.generate_roadmap(
            role=request.role, current_stack=request.current_stack, goal=request.goal,
            hours=request.hours_per_week, learning_style=request.learning_style,
            focus=request.focus, constraints=request.constraints
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")

    # ШАГ 1: Создаем главный объект Career
    meta = ai_data.get("roadmap_meta", {})
    new_career = Career(
        user_id=current_user.id, title=meta.get("title", "Untitled Roadmap"),
        description=meta.get("description", ""), difficulty=meta.get("difficulty", "Intermediate"),
        total_estimated_hours=meta.get("total_estimated_hours", 0),
        total_weeks=meta.get("total_weeks", 0), focus=meta.get("focus", "job-ready"),
        assumptions_json=json.dumps(meta.get("assumptions", []))
    )
    db.add(new_career)
    db.commit()
    db.refresh(new_career)

    # ШАГ 2: Сохраняем все вложенные данные (Milestones, Modules и т.д.)
    if "milestones" in meta:
        for ms_data in meta["milestones"]:
            db.add(Milestone(
                career_id=new_career.id, name=ms_data.get("name"),
                modules_json=json.dumps(ms_data.get("modules", [])), outcome=ms_data.get("outcome")
            ))

    if "modules" in ai_data:
        for module_data in ai_data["modules"]:
            new_module = Module(
                career_id=new_career.id, module_id_str=module_data.get("module_id"),
                depends_on_json=json.dumps(module_data.get("depends_on", [])),
                topic=module_data.get("topic"), goal=module_data.get("goal"),
                estimated_hours=module_data.get("estimated_hours", 0)
            )
            db.add(new_module)
            db.commit()  # Коммитим модуль, чтобы получить его ID для связей
            db.refresh(new_module)

            for res_data in module_data.get("resources", []):
                db.add(Resource(module_id=new_module.id, **res_data))

            pt_data = module_data.get("practice_task")
            if pt_data:
                db.add(PracticeTask(
                    module_id=new_module.id, title=pt_data.get("title"), description=pt_data.get("description"),
                    deliverables_json=json.dumps(pt_data.get("deliverables", [])),
                    acceptance_criteria_json=json.dumps(pt_data.get("acceptance_criteria", []))
                ))

            cp_data = module_data.get("checkpoint")
            if cp_data:
                db.add(Checkpoint(
                    module_id=new_module.id, what_to_show=cp_data.get("what_to_show"),
                    how_to_self_check=cp_data.get("how_to_self_check"),
                    rubric_json=json.dumps(cp_data.get("rubric", []))
                ))

            for q_data in module_data.get("quiz", []):
                db.add(Question(
                    module_id=new_module.id, question_text=q_data.get("question"),
                    options_json=json.dumps(q_data.get("options", [])),
                    correct_index=q_data.get("correct_index"), explanation=q_data.get("explanation")
                ))

    db.commit()  # Сохраняем все добавленные ресурсы, вопросы и т.д.

    # ШАГ 3: Теперь, когда ВСЕ данные в базе, собираем ответ
    db.refresh(new_career)  # Обновляем new_career, чтобы SQLAlchemy подтянул все связи

    meta_response = RoadmapMetaResponse.from_orm(new_career)
    modules_response = [ModuleResponse.from_orm(m) for m in new_career.modules]
    milestones_response = [MilestoneResponse.from_orm(m) for m in new_career.milestones]

    # ШАГ 4: Возвращаем ПРАВИЛЬНЫЙ объект, который соответствует схеме
    return CareerResponseV2(
        roadmap_meta=meta_response,
        modules=modules_response,
        milestones=milestones_response
    )