"""Роутер для публичного API проектов"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from app.database import Project, Tweak, SessionDep
from app.schemas import ProjectResponse
from app.utils import project_to_dict, get_tech_icon, TWEAK_CATEGORIES

router = APIRouter(tags=["projects"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: SessionDep):
    """Главная страница - лендинг с проектами"""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    tweaks = db.query(Tweak).order_by(Tweak.created_at.desc()).all()

    # Преобразуем проекты для шаблона
    projects_data = [project_to_dict(project) for project in projects]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects_data,
            "tweaks": tweaks,
            "tweak_categories": TWEAK_CATEGORIES,
            "get_tech_icon": get_tech_icon,
        }
    )


@router.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(db: SessionDep):
    """JSON API для получения всех проектов"""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects