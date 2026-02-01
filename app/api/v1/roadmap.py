# app/api/v1/roadmap.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.roadmap import Career
from app.schemas.roadmap import CareerResponse
from app.api import deps # Наша новая зависимость

router = APIRouter()

# Получить список всех доступных карьер
# Этот роут открытый (можно без токена, чтобы завлечь юзера), но можно и закрыть
@router.get("/", response_model=List[CareerResponse])
def get_all_careers(db: Session = Depends(deps.get_db)):
    careers = db.query(Career).all()
    return careers

# Получить конкретный роадмап по ID
# Требует токен (current_user), потому что позже будем подмешивать прогресс
@router.get("/{career_id}", response_model=CareerResponse)
def get_career_details(
    career_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user) # <-- Проверка токена!
):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    return career