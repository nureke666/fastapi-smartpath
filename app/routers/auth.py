from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.security import verify_password, create_access_token
from app.db.mock_db import get_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse("login.html", {
            "request": request, "error": "Invalid credentials"
        })

    token = create_access_token(data={"sub": username})

    # Редирект на "Root" логику, которая сама решит, куда пускать юзера
    response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response