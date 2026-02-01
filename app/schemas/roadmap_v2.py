# app/schemas/roadmap_v2.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# --- Схема запроса на генерацию ---
class RoadmapGenerateRequestV2(BaseModel):
    role: str
    current_stack: str = ""
    goal: str
    hours_per_week: int
    learning_style: str = "Mixed"
    focus: str = "job-ready"
    constraints: str = "free-only"


# --- Схемы для ответа (Response Schemas) ---
# Начинаем с самых вложенных элементов

class ResourceResponse(BaseModel):
    title: str
    type: str
    url: str
    search_query: Optional[str] = None
    level: Optional[str] = None
    why_this: Optional[str] = None
    time_estimate_hours: Optional[int] = 0

    class Config:
        from_attributes = True
        orm_mode = True


class PracticeTaskResponse(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deliverables_json: Optional[str] = None
    acceptance_criteria_json: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True


class CheckpointResponse(BaseModel):
    what_to_show: Optional[str] = None
    how_to_self_check: Optional[str] = None
    rubric_json: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True


class QuestionResponse(BaseModel):
    question_text: str
    options_json: str
    correct_index: int
    explanation: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True


class ModuleResponse(BaseModel):
    module_id_str: str
    depends_on_json: str
    topic: str
    goal: str
    estimated_hours: int
    resources: List[ResourceResponse] = []
    practice_task: Optional[PracticeTaskResponse] = None
    checkpoint: Optional[CheckpointResponse] = None
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True
        orm_mode = True


class MilestoneResponse(BaseModel):
    name: str
    modules_json: str
    outcome: str

    class Config:
        from_attributes = True
        orm_mode = True


class RoadmapMetaResponse(BaseModel):
    title: str
    description: str
    difficulty: str
    total_estimated_hours: int
    total_weeks: int
    focus: str
    assumptions_json: str

    class Config:
        from_attributes = True
        orm_mode = True


# --- Главная схема ответа ---
class CareerResponseV2(BaseModel):
    roadmap_meta: RoadmapMetaResponse
    modules: List[ModuleResponse] = []
    milestones: List[MilestoneResponse] = []

    class Config:
        from_attributes = True
        orm_mode = True
