# app/db/mock_db.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Имитация базы данных (храним в памяти)
# Структура: username -> { данные }
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin"),
        "role_goal": None,
        "roadmap_data": None,
        "is_onboarded": False
    }
}


def get_user(username: str):
    """Поиск по username"""
    return users_db.get(username)


def get_user_by_email(email: str):
    """Поиск по email"""
    for user in users_db.values():
        if user.get("email") == email:
            return user
    return None


def create_user(username: str, email: str, password: str):
    """Создание нового пользователя"""
    if username in users_db:
        return None  # Пользователь уже есть

    hashed_password = pwd_context.hash(password)

    new_user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role_goal": None,
        "roadmap_data": None,
        "is_onboarded": False
    }

    users_db[username] = new_user
    return new_user


def update_user_roadmap(username: str, role: str, roadmap: list):
    if username in users_db:
        users_db[username]["role_goal"] = role
        users_db[username]["roadmap_data"] = roadmap
        users_db[username]["is_onboarded"] = True