# app/schemas/roadmap.py
from pydantic import BaseModel
from typing import List, Optional


# --- Nodes (Узлы/Темы) ---
class RoadmapGenerateRequest(BaseModel):
    target_role: str       # Кем хочет стать (Python Dev)
    current_experience: str # Опыт (Знаю SQL, но не знаю Python)
    goal: str              # Цель (Найти работу через 3 месяца)
    hours_per_week: int    # Сколько времени есть (10)

class RoadmapNodeBase(BaseModel):
    title: str
    description_content: Optional[str] = None
    order_index: int


class RoadmapNodeResponse(RoadmapNodeBase):
    id: int
    status: str = "LOCKED"

    # Позже добавим сюда статус (LOCKED/OPEN), пока просто данные

    class Config:
        from_attributes = True


# --- Careers (Карьеры) ---
class CareerBase(BaseModel):
    title: str
    description: Optional[str] = None


class CareerResponse(CareerBase):
    id: int
    nodes: List[RoadmapNodeResponse] = []

    class Config:
        from_attributes = True