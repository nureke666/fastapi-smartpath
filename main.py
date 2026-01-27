import json
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, List, Optional

from fastapi import FastAPI, Form, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from google import genai
from google.genai import types
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import API_KEY1, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="SmartPath MVP")
templates = Jinja2Templates(directory="templates")

# Настройка безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Инициализация Gemini
client = genai.Client(api_key=API_KEY1)

# --- ФЕЙКОВАЯ БАЗА ДАННЫХ ---
# Пароль для admin: "admin" (захеширован)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin"),
        "disabled": False,
    }
}


# --- ФУНКЦИИ БЕЗОПАСНОСТИ ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Убираем префикс Bearer если есть
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    return username


# --- РОУТЫ (PAGES) ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница логина"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Обработка входа"""
    user = fake_users_db.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    # Перенаправляем на дашборд и ставим куку
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Форма ввода данных (доступна только после входа)"""
    user = await get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.post("/generate", response_class=HTMLResponse)
async def generate_roadmap(
        request: Request,
        role: Annotated[str, Form()],
        experience: Annotated[str, Form()]
):
    """Генерация карты (Защищена)"""
    user = await get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/")

    # Промпт для AI
    prompt = f"""
    Ты карьерный ментор. Роль: {role}. Уровень: {experience}.
    Создай JSON роадмап (5 шагов).
    ВЕРНИ ТОЛЬКО JSON список:
    [
      {{"step": "Название", "description": "Описание", "time": "Срок"}}
    ]
    """

    roadmap_data = []
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        # Чистка
        text = response.text.replace("```json", "").replace("```", "").strip()
        roadmap_data = json.loads(text)
    except Exception:
        roadmap_data = [{"step": "Error", "description": "AI Error", "time": "0m"}]

    return templates.TemplateResponse("roadmap.html", {
        "request": request,
        "roadmap": roadmap_data,
        "role": role
    })