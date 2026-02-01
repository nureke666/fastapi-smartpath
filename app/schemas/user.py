# app/schemas/user.py
from pydantic import BaseModel, EmailStr

# Базовая схема
class UserBase(BaseModel):
    email: EmailStr

# То, что юзер шлет при регистрации
class UserCreate(UserBase):
    password: str

# То, что мы отдаем юзеру обратно (без пароля!)
class UserResponse(UserBase):
    id: int
    username: str | None = None

    class Config:
        from_attributes = True # Чтобы Pydantic читал данные из SQLAlchemy моделей