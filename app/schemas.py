"""Pydantic схемы для валидации данных"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class TechStackItem(BaseModel):
    """Элемент технологического стека"""
    name: str
    value: str


class ProjectBase(BaseModel):
    """Базовая схема проекта"""
    title: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=200)
    results: List[str] = Field(..., min_items=1)
    timeline: str = Field(..., min_length=1, max_length=100)
    budget: str = Field(..., min_length=1, max_length=100)
    benefits: str = Field(..., min_length=1)
    tech_stack: Dict[str, str] = Field(default_factory=dict)
    images: Optional[List[str]] = None


class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""
    pass


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = Field(None, min_length=1, max_length=200)
    results: Optional[List[str]] = Field(None, min_items=1)
    timeline: Optional[str] = Field(None, min_length=1, max_length=100)
    budget: Optional[str] = Field(None, min_length=1, max_length=100)
    benefits: Optional[str] = Field(None, min_length=1)
    tech_stack: Optional[Dict[str, str]] = None
    images: Optional[List[str]] = None


class ProjectResponse(ProjectBase):
    """Схема ответа с проектом"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TweakBase(BaseModel):
    """Базовая схема мелкой доработки"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=50)
    project_name: Optional[str] = Field(None, max_length=200)
    time_spent: Optional[str] = Field(None, max_length=100)


class TweakResponse(TweakBase):
    """Схема ответа с доработкой"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Схема для входа"""
    password: str