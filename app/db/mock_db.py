from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Имитация базы данных
# Структура: username -> {данные}
users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin"),
        "role_goal": None,      # Кем хочет стать (сохраним после опроса)
        "roadmap_data": None,   # Сама карта (JSON)
        "is_onboarded": False   # Прошел ли опрос?
    },
    "student": {
        "username": "student",
        "full_name": "Student User",
        "hashed_password": pwd_context.hash("123"),
        "role_goal": None,
        "roadmap_data": None,
        "is_onboarded": False
    }
}

def get_user(username: str):
    return users_db.get(username)

def update_user_roadmap(username: str, role: str, roadmap: list):
    if username in users_db:
        users_db[username]["role_goal"] = role
        users_db[username]["roadmap_data"] = roadmap
        users_db[username]["is_onboarded"] = True