from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, navigation

app = FastAPI(title="SmartPath MVP")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(navigation.router)

# Если будут картинки/стили
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)