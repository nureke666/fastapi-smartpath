# app/routers/auth.py
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.security import verify_password, create_access_token
from app.db.mock_db import get_user, create_user, get_user_by_email
from app.services.email import send_email_simulation

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")


# --- СТРАНИЦЫ (FRONTEND - пока заглушки) ---

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# --- API ENDPOINTS (SPRINT 1) ---

@router.post("/auth/register")
async def register(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    # 1. Проверяем, есть ли такой юзер
    if get_user(username):
        return JSONResponse(
            status_code=400,
            content={"error": "Пользователь с таким username уже существует"}
        )

    if get_user_by_email(email):
        return JSONResponse(
            status_code=400,
            content={"error": "Пользователь с таким email уже существует"}
        )

    # 2. Создаем юзера
    user = create_user(username, email, password)

    # 3. Отправляем письмо (Имитация)
    send_email_simulation(
        to_email=email,
        subject="Добро пожаловать в SmartPath!",
        body=f"Привет, {username}! Спасибо за регистрацию. Твой путь в IT начинается здесь."
    )

    return JSONResponse(
        status_code=201,
        content={"message": "Пользователь успешно создан. Проверьте консоль на наличие письма."}
    )


@router.post("/auth/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    user = get_user(username)

    if not user or not verify_password(password, user["hashed_password"]):
        # Если запрос пришел AJAX-ом (API), возвращаем JSON ошибку
        # Если с браузера - можно вернуть HTML, но сейчас у нас фокус на API
        return JSONResponse(
            status_code=401,
            content={"error": "Неверный логин или пароль"}
        )

    # Создаем токен
    token = create_access_token(data={"sub": username})

    # Создаем редирект (как в старом коде), но добавляем инфо в тело ответа
    response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)

    return response


@router.post("/auth/forgot-password")
async def forgot_password(email: str = Form(...)):
    user = get_user_by_email(email)

    if not user:
        # По безопасности лучше не говорить, что почты нет, но для MVP скажем
        return JSONResponse(
            status_code=404,
            content={"error": "Пользователь с таким email не найден"}
        )

    # Имитация ссылки сброса
    reset_link = f"http://localhost:8000/reset-password?token=fake_token_for_{user['username']}"

    send_email_simulation(
        to_email=email,
        subject="Сброс пароля SmartPath",
        body=f"Кто-то запросил сброс пароля. Если это вы, перейдите по ссылке:\n{reset_link}"
    )

    return JSONResponse(
        status_code=200,
        content={"message": "Инструкция по сбросу пароля отправлена на email."}
    )


@router.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response