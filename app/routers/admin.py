"""Роутер для админ-панели"""
from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import os
from datetime import datetime

from app.database import Project, Tweak, SessionDep
from app.auth import verify_password, ADMIN_SESSION_KEY, AdminDep
from app.config import settings
from app.utils import (
    project_to_dict,
    parse_form_results,
    parse_form_tech_stack,
    save_uploaded_images,
    parse_existing_images,
    TWEAK_CATEGORIES,
)
from app.llm import generate_project_with_llm, generate_tweak_with_llm, get_github_repo_info

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


def ensure_upload_dir():
    """Создать директорию для загрузок если её нет"""
    os.makedirs(settings.upload_dir, exist_ok=True)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа админа"""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    password: str = Form(...)
):
    """Вход админа"""
    if verify_password(password):
        request.session[ADMIN_SESSION_KEY] = True
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Неверный пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@router.get("/logout")
async def logout(request: Request):
    """Выход админа"""
    request.session.pop(ADMIN_SESSION_KEY, None)
    return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: SessionDep, admin: AdminDep):
    """Дашборд со списком проектов"""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    tweaks = db.query(Tweak).order_by(Tweak.created_at.desc()).all()

    projects_data = [
        {
            "id": project.id,
            "title": project.title,
            "industry": project.industry,
            "created_at": project.created_at,
        }
        for project in projects
    ]

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "projects": projects_data,
            "tweaks": tweaks,
            "tweak_categories": TWEAK_CATEGORIES,
        }
    )


@router.get("/projects/new", response_class=HTMLResponse)
async def new_project_form(request: Request, admin: AdminDep):
    """Форма создания нового проекта"""
    return templates.TemplateResponse("admin/project_form.html", {
        "request": request,
        "project": None,
        "is_edit": False
    })


@router.post("/projects/generate", response_class=HTMLResponse)
async def generate_project_from_text(
    request: Request,
    admin: AdminDep,
    description: str = Form(...)
):
    """Генерация проекта через LLM на основе текстового описания"""
    try:
        if not settings.openai_key:
            return templates.TemplateResponse("admin/project_form.html", {
                "request": request,
                "project": None,
                "is_edit": False,
                "error": "OPENAI_KEY не настроен в .env"
            })
        
        generated_data = generate_project_with_llm(description)
        
        # Форматирование результатов для формы
        results_text = "\n".join(generated_data.get("results", []))
        
        return templates.TemplateResponse("admin/project_form.html", {
            "request": request,
            "project": {
                "title": generated_data.get("title", ""),
                "industry": generated_data.get("industry", ""),
                "results": generated_data.get("results", []),
                "timeline": generated_data.get("timeline", ""),
                "budget": generated_data.get("budget", ""),
                "benefits": generated_data.get("benefits", ""),
                "tech_stack": generated_data.get("tech_stack", {})
            },
            "is_edit": False,
            "generated": True
        })
    except Exception as e:
        return templates.TemplateResponse("admin/project_form.html", {
            "request": request,
            "project": None,
            "is_edit": False,
            "error": f"Ошибка при генерации проекта: {str(e)}"
        })


@router.post("/projects/generate-from-github", response_class=HTMLResponse)
async def generate_project_from_github(
    request: Request,
    admin: AdminDep,
    github_url: str = Form(...)
):
    """Генерация проекта через LLM на основе GitHub репозитория"""
    try:
        if not settings.openai_key:
            return templates.TemplateResponse("admin/project_form.html", {
                "request": request,
                "project": None,
                "is_edit": False,
                "error": "OPENAI_KEY не настроен в .env"
            })
        
        # Получение информации о репозитории
        repo_info = get_github_repo_info(github_url)
        if not repo_info:
            return templates.TemplateResponse("admin/project_form.html", {
                "request": request,
                "project": None,
                "is_edit": False,
                "error": "Не удалось получить информацию о репозитории. Проверьте URL."
            })
        
        # Генерация проекта на основе информации о репозитории
        generated_data = generate_project_with_llm(repo_info)
        
        return templates.TemplateResponse("admin/project_form.html", {
            "request": request,
            "project": {
                "title": generated_data.get("title", ""),
                "industry": generated_data.get("industry", ""),
                "results": generated_data.get("results", []),
                "timeline": generated_data.get("timeline", ""),
                "budget": generated_data.get("budget", ""),
                "benefits": generated_data.get("benefits", ""),
                "tech_stack": generated_data.get("tech_stack", {})
            },
            "is_edit": False,
            "generated": True
        })
    except Exception as e:
        return templates.TemplateResponse("admin/project_form.html", {
            "request": request,
            "project": None,
            "is_edit": False,
            "error": f"Ошибка при генерации проекта: {str(e)}"
        })


@router.post("/projects")
async def create_project(
    request: Request,
    db: SessionDep,
    admin: AdminDep,
    title: str = Form(...),
    industry: str = Form(...),
    results: str = Form(...),
    timeline: str = Form(...),
    budget: str = Form(...),
    benefits: str = Form(...),
    tech_stack_keys: Optional[List[str]] = Form(default=None),
    tech_stack_values: Optional[List[str]] = Form(default=None),
    images: List[UploadFile] = File(default=[])
):
    """Создание нового проекта"""
    ensure_upload_dir()
    
    # Парсинг данных из формы
    results_list = parse_form_results(results)
    tech_stack_dict = parse_form_tech_stack(tech_stack_keys, tech_stack_values)
    image_paths = save_uploaded_images(images)
    
    # Создание проекта
    project = Project(
        title=title,
        industry=industry,
        timeline=timeline,
        budget=budget,
        benefits=benefits
    )
    project.set_results_list(results_list)
    project.set_tech_stack_dict(tech_stack_dict)
    if image_paths:
        project.set_images_list(image_paths)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)


@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(
    request: Request,
    project_id: int,
    db: SessionDep,
    admin: AdminDep
):
    """Форма редактирования проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    project_data = project_to_dict(project)
    
    return templates.TemplateResponse("admin/project_form.html", {
        "request": request,
        "project": project_data,
        "is_edit": True
    })


@router.post("/projects/{project_id}")
async def update_project(
    request: Request,
    project_id: int,
    db: SessionDep,
    admin: AdminDep,
    title: str = Form(...),
    industry: str = Form(...),
    results: str = Form(...),
    timeline: str = Form(...),
    budget: str = Form(...),
    benefits: str = Form(...),
    tech_stack_keys: Optional[List[str]] = Form(default=None),
    tech_stack_values: Optional[List[str]] = Form(default=None),
    images: List[UploadFile] = File(default=[]),
    existing_images: Optional[str] = Form(default=None)
):
    """Обновление проекта"""
    ensure_upload_dir()
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Парсинг данных из формы
    results_list = parse_form_results(results)
    tech_stack_dict = parse_form_tech_stack(tech_stack_keys, tech_stack_values)
    
    # Сохранение изображений
    image_paths = parse_existing_images(existing_images)
    image_paths.extend(save_uploaded_images(images))
    
    # Обновление проекта
    project.title = title
    project.industry = industry
    project.timeline = timeline
    project.budget = budget
    project.benefits = benefits
    project.set_results_list(results_list)
    project.set_tech_stack_dict(tech_stack_dict)
    project.set_images_list(image_paths)
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)


@router.post("/projects/{project_id}/delete")
async def delete_project(
    request: Request,
    project_id: int,
    db: SessionDep,
    admin: AdminDep
):
    """Удаление проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Удаление изображений
    images = project.get_images_list()
    for image_path in images:
        full_path = os.path.join("app/static", image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    
    db.delete(project)
    db.commit()

    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)


# ==================== Мелкие доработки ====================

@router.get("/tweaks/new", response_class=HTMLResponse)
async def new_tweak_form(request: Request, admin: AdminDep):
    """Форма создания новой доработки"""
    return templates.TemplateResponse("admin/tweak_form.html", {
        "request": request,
        "tweak": None,
        "is_edit": False,
        "tweak_categories": TWEAK_CATEGORIES,
    })


@router.post("/tweaks/generate", response_class=HTMLResponse)
async def generate_tweak_from_text(
    request: Request,
    admin: AdminDep,
    description: str = Form(...)
):
    """Генерация доработки через LLM на основе текстового описания"""
    try:
        if not settings.openai_key:
            return templates.TemplateResponse("admin/tweak_form.html", {
                "request": request,
                "tweak": None,
                "is_edit": False,
                "tweak_categories": TWEAK_CATEGORIES,
                "error": "OPENAI_KEY не настроен в .env",
            })

        generated_data = generate_tweak_with_llm(description)

        # Создаём объект-заглушку для шаблона
        class TweakData:
            pass

        tweak_data = TweakData()
        tweak_data.title = generated_data.get("title", "")
        tweak_data.description = generated_data.get("description", "")
        tweak_data.category = generated_data.get("category", "other")
        tweak_data.project_name = generated_data.get("project_name")
        tweak_data.time_spent = generated_data.get("time_spent")
        tweak_data.github_url = generated_data.get("github_url")

        return templates.TemplateResponse("admin/tweak_form.html", {
            "request": request,
            "tweak": tweak_data,
            "is_edit": False,
            "tweak_categories": TWEAK_CATEGORIES,
            "generated": True,
        })
    except Exception as e:
        return templates.TemplateResponse("admin/tweak_form.html", {
            "request": request,
            "tweak": None,
            "is_edit": False,
            "tweak_categories": TWEAK_CATEGORIES,
            "error": f"Ошибка при генерации: {str(e)}",
        })


@router.post("/tweaks")
async def create_tweak(
    request: Request,
    db: SessionDep,
    admin: AdminDep,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    project_name: Optional[str] = Form(default=None),
    time_spent: Optional[str] = Form(default=None),
    github_url: Optional[str] = Form(default=None),
):
    """Создание новой доработки"""
    tweak = Tweak(
        title=title,
        description=description,
        category=category,
        project_name=project_name if project_name and project_name.strip() else None,
        time_spent=time_spent if time_spent and time_spent.strip() else None,
        github_url=github_url if github_url and github_url.strip() else None,
    )
    db.add(tweak)
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)


@router.get("/tweaks/{tweak_id}/edit", response_class=HTMLResponse)
async def edit_tweak_form(
    request: Request,
    tweak_id: int,
    db: SessionDep,
    admin: AdminDep,
):
    """Форма редактирования доработки"""
    tweak = db.query(Tweak).filter(Tweak.id == tweak_id).first()
    if not tweak:
        raise HTTPException(status_code=404, detail="Доработка не найдена")

    return templates.TemplateResponse("admin/tweak_form.html", {
        "request": request,
        "tweak": tweak,
        "is_edit": True,
        "tweak_categories": TWEAK_CATEGORIES,
    })


@router.post("/tweaks/{tweak_id}")
async def update_tweak(
    request: Request,
    tweak_id: int,
    db: SessionDep,
    admin: AdminDep,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    project_name: Optional[str] = Form(default=None),
    time_spent: Optional[str] = Form(default=None),
    github_url: Optional[str] = Form(default=None),
):
    """Обновление доработки"""
    tweak = db.query(Tweak).filter(Tweak.id == tweak_id).first()
    if not tweak:
        raise HTTPException(status_code=404, detail="Доработка не найдена")

    tweak.title = title
    tweak.description = description
    tweak.category = category
    tweak.project_name = project_name if project_name and project_name.strip() else None
    tweak.time_spent = time_spent if time_spent and time_spent.strip() else None
    tweak.github_url = github_url if github_url and github_url.strip() else None
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)


@router.post("/tweaks/{tweak_id}/delete")
async def delete_tweak(
    request: Request,
    tweak_id: int,
    db: SessionDep,
    admin: AdminDep,
):
    """Удаление доработки"""
    tweak = db.query(Tweak).filter(Tweak.id == tweak_id).first()
    if not tweak:
        raise HTTPException(status_code=404, detail="Доработка не найдена")

    db.delete(tweak)
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)