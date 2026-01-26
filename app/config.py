"""Конфигурация приложения"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Безопасность
    admin_password: str = "admin123"
    """Пароль администратора. Должен быть изменен в .env для продакшена"""
    
    secret_key: str = "your-secret-key-change-in-production"
    """Секретный ключ для сессий. Должен быть изменен в .env для продакшена"""
    
    # База данных
    database_url: str = "sqlite:///./projects.db"
    """URL подключения к базе данных"""
    
    # Файлы
    upload_dir: str = "app/static/uploads"
    """Директория для загрузки файлов"""
    
    # CORS
    cors_origins: str = "*"
    """Разрешенные источники для CORS. Для продакшена указать конкретные домены через запятую"""
    
    # OpenAI
    openai_key: Optional[str] = None
    """API ключ OpenAI для генерации проектов через LLM"""
    
    # Порт приложения
    port: int = 8000
    """Порт для запуска приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )
    
    def get_cors_origins(self) -> List[str]:
        """Получить список разрешенных CORS origins"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()