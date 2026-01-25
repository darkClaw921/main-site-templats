"""Система аутентификации админа"""
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from app.config import settings


# Простая проверка пароля через сессию
ADMIN_SESSION_KEY = "admin_authenticated"


def verify_password(password: str) -> bool:
    """Проверка пароля админа"""
    return password == settings.admin_password


def check_admin_session(request: Request) -> bool:
    """Проверка сессии админа"""
    return request.session.get(ADMIN_SESSION_KEY, False)


def require_admin(request: Request) -> bool:
    """Зависимость для защиты админских роутов"""
    if not check_admin_session(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация администратора",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


# Типизация для dependency injection
AdminDep = Annotated[bool, Depends(require_admin)]