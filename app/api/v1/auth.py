# app/api/v1/auth.py
from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import SessionLocal
from app.models.user import User
from app.models.roadmap import UserProgress, Module
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.api import deps # Используем общие зависимости


router = APIRouter()

# --- Schemas for Profile ---
class Badge(BaseModel):
    name: str
    icon: str
    description: str

class UserProfile(UserResponse):
    level: int
    xp: int
    completed_modules: int
    total_modules_started: int
    badges: List[Badge]

# --- Endpoints ---

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        username=user_in.email.split("@")[0]
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login_for_access_token(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserProfile)
def read_users_me(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    # 1. Считаем статистику
    progress_items = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()

    completed_count = sum(1 for p in progress_items if p.status == "COMPLETED")
    total_started = len(progress_items)

    # 2. Геймификация (простая логика)
    # 1 модуль = 100 XP
    xp = completed_count * 100

    # Уровень: каждые 500 XP новый уровень (1 -> 5 модулей)
    level = 1 + (xp // 500)

    # 3. Ачивки (Badges)
    badges = []

    # Бейдж "Новичок" - за регистрацию (всегда есть)
    badges.append(Badge(name="Explorer", icon="hiking", description="Started the journey"))

    if completed_count >= 1:
        badges.append(Badge(name="First Step", icon="flag", description="Completed first module"))

    if completed_count >= 5:
        badges.append(Badge(name="High Five", icon="sentiment_satisfied_alt", description="Completed 5 modules"))

    if completed_count >= 10:
        badges.append(Badge(name="Dedicated", icon="local_fire_department", description="Completed 10 modules"))

    if level >= 5:
        badges.append(Badge(name="Pro", icon="school", description="Reached Level 5"))

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "level": level,
        "xp": xp,
        "completed_modules": completed_count,
        "total_modules_started": total_started,
        "badges": badges
    }
