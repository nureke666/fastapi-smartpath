# app/schemas/roadmap.py
from pydantic import BaseModel
from typing import List, Optional


# --- Resources ---
class ResourceResponse(BaseModel):
    title: str
    type: str
    url: str
    level: Optional[str] = None
    why_this: Optional[str] = None

    class Config:
        from_attributes = True


# --- Nodes ---
class RoadmapNodeBase(BaseModel):
    title: str
    description_content: Optional[str] = None
    summary: Optional[str] = None # <-- НОВОЕ ПОЛЕ
    order_index: int


class RoadmapNodeResponse(RoadmapNodeBase):
    id: int
    status: str = "LOCKED"
    resources: List[ResourceResponse] = []

    class Config:
        from_attributes = True


# --- Careers ---
class CareerBase(BaseModel):
    title: str
    description: Optional[str] = None


class CareerResponse(CareerBase):
    id: int
    nodes: List[RoadmapNodeResponse] = []

    class Config:
        from_attributes = True


class RoadmapGenerateRequest(BaseModel):
    target_role: str
    current_experience: str
    goal: str
    hours_per_week: int