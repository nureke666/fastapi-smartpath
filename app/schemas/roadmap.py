# app/schemas/roadmap.py
from pydantic import BaseModel
from typing import List, Optional


# --- Nodes (Узлы/Темы) ---
class RoadmapNodeBase(BaseModel):
    title: str
    description_content: Optional[str] = None
    order_index: int


class RoadmapNodeResponse(RoadmapNodeBase):
    id: int

    # Позже добавим сюда статус (LOCKED/OPEN), пока просто данные

    class Config:
        from_attributes = True


# --- Careers (Карьеры) ---
class CareerBase(BaseModel):
    title: str
    description: Optional[str] = None


class CareerResponse(CareerBase):
    id: int
    # В ответе карьеры мы хотим сразу видеть список тем
    nodes: List[RoadmapNodeResponse] = []

    class Config:
        from_attributes = True