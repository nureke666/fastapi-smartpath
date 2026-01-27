from fastapi import APIRouter, Request, Form, Depends, Body
from app.services.ai_generator import generate_roadmap_ai
from app.db.mock_db import update_user_roadmap
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse # Добавили JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.security import get_current_user
from app.services.ai_generator import client, types

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/app")
async def main_app_logic(request: Request, user: dict = Depends(get_current_user)):
    """Умный редирект"""
    if not user:
        return RedirectResponse("/")

    # Если юзер уже прошел опрос -> показываем карту
    if user["is_onboarded"]:
        return RedirectResponse("/roadmap")

    # Если не прошел -> показываем опрос
    return RedirectResponse("/onboarding")


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request, user: dict = Depends(get_current_user)):
    if not user: return RedirectResponse("/")
    return templates.TemplateResponse("onboarding.html", {"request": request, "user": user})


@router.post("/process-onboarding")
async def process_onboarding(
        request: Request,
        role: str = Form(...),
        experience: str = Form(...),
        time: str = Form(...),
        user: dict = Depends(get_current_user)
):
    """Принимаем ответы, генерируем AI, сохраняем в БД"""
    if not user: return RedirectResponse("/")

    # 1. Спрашиваем AI
    roadmap = generate_roadmap_ai(role, experience, time)

    # 2. Сохраняем в БД навсегда (пока сервер не перезагрузят)
    update_user_roadmap(user["username"], role, roadmap)

    # 3. Ведем на карту
    return RedirectResponse("/roadmap", status_code=302)


@router.get("/market", response_class=HTMLResponse)
async def market_page(request: Request, user: dict = Depends(get_current_user)):
    if not user: return RedirectResponse("/")
    return templates.TemplateResponse("market.html", {"request": request, "user": user})

@router.get("/assessment", response_class=HTMLResponse)
async def assessment_page(request: Request, user: dict = Depends(get_current_user)):
    if not user: return RedirectResponse("/")
    return templates.TemplateResponse("assessment.html", {"request": request, "user": user})

@router.get("/upgrade", response_class=HTMLResponse)
async def upgrade_page(request: Request, user: dict = Depends(get_current_user)):
    if not user: return RedirectResponse("/")
    return templates.TemplateResponse("upgrade.html", {"request": request, "user": user})

@router.get("/roadmap", response_class=HTMLResponse)
async def show_roadmap(request: Request, user: dict = Depends(get_current_user)):
    if not user: return RedirectResponse("/")

    # Если попытался зайти сюда без опроса -> назад
    if not user["is_onboarded"]:
        return RedirectResponse("/onboarding")

    return templates.TemplateResponse("roadmap.html", {
        "request": request,
        "roadmap": user["roadmap_data"],
        "role": user["role_goal"],
        "user": user
    })


@router.post("/api/chat")
async def chat_api(
        data: dict = Body(...),
        user: dict = Depends(get_current_user)
):
    """Принимает вопрос JSON, возвращает ответ AI"""
    if not user: return JSONResponse({"error": "Unauthorized"}, status_code=401)

    question = data.get("message", "")
    role = user.get("role_goal", "Developer")

    prompt = f"Ты карьерный коуч. Пользователь учится на {role}. Он спрашивает: '{question}'. Ответь кратко (макс 2 предложения), мотивирующе."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return JSONResponse({"answer": response.text})
    except Exception as e:
        return JSONResponse({"answer": "AI is currently offline. Try again later."})