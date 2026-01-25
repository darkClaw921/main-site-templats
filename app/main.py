"""Главный файл FastAPI приложения"""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db
from app.routers.projects import router as projects_router
from app.routers.admin import router as admin_router


# Инициализация приложения
app = FastAPI(
    title="Alteran Portfolio",
    description="Лендинг с портфолио проектов и админ-панелью",
    version="1.0.0"
)

# Инициализация при старте приложения
@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    os.makedirs(settings.upload_dir, exist_ok=True)
    init_db()

# Подключение middleware для сессий
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key
)

# Подключение CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключение роутеров
app.include_router(projects_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)