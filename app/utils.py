"""Утилиты для работы с проектами"""
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import UploadFile
import os
import shutil
import zipfile
import io
import uuid

from app.database import Project
from app.config import settings


def project_to_dict(project: Project) -> dict:
    """Преобразовать модель Project в словарь для шаблонов"""
    try:
        tech_stack = project.get_tech_stack_dict()
    except Exception:
        # Если не удалось распарсить tech_stack, возвращаем пустой словарь
        tech_stack = {}
    
    return {
        "id": project.id,
        "title": project.title,
        "industry": project.industry,
        "results": project.get_results_list(),
        "timeline": project.timeline,
        "budget": project.budget,
        "benefits": project.benefits,
        "tech_stack": tech_stack,
        "images": project.get_images_list(),
        "mockups": project.get_mockups_list(),
        "github_url": project.github_url,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


def parse_form_results(results: str) -> List[str]:
    """Парсинг результатов из формы (разделены новой строкой)"""
    return [r.strip() for r in results.split("\n") if r.strip()]


def parse_form_tech_stack(
    tech_stack_keys: Optional[List[str]],
    tech_stack_values: Optional[List[str]]
) -> Dict[str, str]:
    """Парсинг технологического стека из формы"""
    tech_stack_dict = {}
    if tech_stack_keys and tech_stack_values:
        for key, value in zip(tech_stack_keys, tech_stack_values):
            if key and value and key.strip() and value.strip():
                tech_stack_dict[key.strip()] = value.strip()
    return tech_stack_dict


def save_uploaded_images(images: List[UploadFile]) -> List[str]:
    """Сохранить загруженные изображения и вернуть список путей"""
    image_paths = []
    for image in images:
        if image.filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{image.filename}"
            file_path = os.path.join(settings.upload_dir, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_paths.append(f"uploads/{filename}")
    return image_paths


def save_mockups_zip(zip_file: Optional[UploadFile]) -> List[str]:
    """Распаковать zip архив, сохранить PNG изображения в uploads/mockups, вернуть пути"""
    if not zip_file or not zip_file.filename:
        return []

    mockups_dir = os.path.join(settings.upload_dir, "mockups")
    os.makedirs(mockups_dir, exist_ok=True)

    mockup_paths: List[str] = []
    # UploadFile может быть уже в конце — сбрасываем позицию
    try:
        zip_file.file.seek(0)
    except Exception:
        pass
    content = zip_file.file.read()
    if not content:
        return []

    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        # Сортировка для стабильного порядка отображения
        names = sorted(n for n in zf.namelist() if not n.endswith("/"))
        idx = 0
        for name in names:
            base = os.path.basename(name)
            if not base:
                continue
            if base.startswith("._"):
                # macOS metadata
                continue
            if not base.lower().endswith(".png"):
                continue
            safe_name = base.replace("\\", "_").replace("/", "_")
            filename = f"{batch_id}_{idx:04d}_{safe_name}"
            idx += 1
            file_path = os.path.join(mockups_dir, filename)
            with zf.open(name) as src, open(file_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            mockup_paths.append(f"uploads/mockups/{filename}")

    return mockup_paths


def parse_existing_mockups(existing_mockups: Optional[str]) -> List[str]:
    """Парсинг существующих макетов из строки формы"""
    paths: List[str] = []
    if existing_mockups:
        for p in existing_mockups.replace("\n", ",").split(","):
            p = p.strip()
            if p:
                paths.append(p)
    return paths


def parse_existing_images(existing_images: Optional[str]) -> List[str]:
    """Парсинг существующих изображений из строки формы"""
    image_paths = []
    if existing_images:
        for img in existing_images.replace('\n', ',').split(','):
            img = img.strip()
            if img:
                image_paths.append(img)
    return image_paths


# Категории мелких доработок с человекочитаемыми названиями
TWEAK_CATEGORIES = {
    "bug_fix": "Исправление бага",
    "ui": "UI улучшение",
    "optimization": "Оптимизация",
    "feature": "Новая функция",
    "refactoring": "Рефакторинг",
    "other": "Другое",
}


def get_tech_icon(tech_category: str) -> Optional[str]:
    """Получить путь к SVG иконке для категории технологии"""
    # Нормализация названия категории (приведение к нижнему регистру)
    category_lower = tech_category.lower().strip()
    
    # Маппинг категорий к файлам иконок
    icon_mapping = {
        'frontend': 'frontend.svg',
        'backend': 'backend.svg',
        'database': 'database.svg',
        'база данных': 'database.svg',
        'mobile': 'mobile.svg',
        'мобильный': 'mobile.svg',
        'devops': 'devops.svg',
        'design': 'design.svg',
        'дизайн': 'design.svg',
        'testing': 'testing.svg',
        'тестирование': 'testing.svg',
        'cloud': 'cloud.svg',
        'облако': 'cloud.svg',
        'api': 'api.svg',
    }
    
    # Проверка точного совпадения
    if category_lower in icon_mapping:
        return f"icons/{icon_mapping[category_lower]}"
    
    # Проверка частичного совпадения (например, "Frontend: Next.js" -> "frontend")
    for key in icon_mapping.keys():
        if key in category_lower:
            return f"icons/{icon_mapping[key]}"
    
    # Если иконка не найдена, возвращаем None
    return None
