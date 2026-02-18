"""База данных и модели SQLAlchemy"""
from typing import Annotated
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Depends
from datetime import datetime
import json

from app.config import settings

# Создание движка базы данных
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Project(Base):
    """Модель проекта"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    industry = Column(String, nullable=False)
    results = Column(Text, nullable=False)  # JSON строка со списком результатов
    timeline = Column(String, nullable=False)
    budget = Column(String, nullable=False)
    benefits = Column(Text, nullable=False)
    tech_stack = Column(Text, nullable=False)  # JSON строка со стеком технологий
    images = Column(Text, nullable=True)  # JSON строка со списком путей к изображениям
    github_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_results_list(self) -> list[str]:
        """Получить список результатов"""
        if self.results:
            return json.loads(self.results)
        return []

    def set_results_list(self, results: list[str]):
        """Установить список результатов"""
        self.results = json.dumps(results, ensure_ascii=False)

    def get_tech_stack_dict(self) -> dict:
        """Получить словарь технологического стека"""
        if self.tech_stack:
            try:
                return json.loads(self.tech_stack)
            except (json.JSONDecodeError, TypeError):
                # Если данные не являются валидным JSON, возвращаем пустой словарь
                return {}
        return {}

    def set_tech_stack_dict(self, tech_stack: dict):
        """Установить словарь технологического стека"""
        self.tech_stack = json.dumps(tech_stack, ensure_ascii=False)

    def get_images_list(self) -> list[str]:
        """Получить список изображений"""
        if self.images:
            return json.loads(self.images)
        return []

    def set_images_list(self, images: list[str]):
        """Установить список изображений"""
        self.images = json.dumps(images, ensure_ascii=False) if images else None


class Tweak(Base):
    """Модель мелкой доработки"""
    __tablename__ = "tweaks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # bug_fix, ui, optimization, feature, refactoring, other
    project_name = Column(String, nullable=True)  # Для какого проекта (опционально)
    time_spent = Column(String, nullable=True)  # Время выполнения ("2 часа", "1 день")
    github_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Инициализация базы данных - создание таблиц"""
    Base.metadata.create_all(bind=engine)
    run_migrations()


def run_migrations():
    """Автоматические миграции — добавление недостающих колонок"""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    migrations = [
        # (table, column, SQL type)
        ("tweaks", "github_url", "TEXT"),
        ("projects", "github_url", "TEXT"),
    ]

    with engine.connect() as conn:
        for table, column, col_type in migrations:
            if table not in inspector.get_table_names():
                continue
            existing = [c["name"] for c in inspector.get_columns(table)]
            if column not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()


def get_db():
    """Получить сессию базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Типизация для dependency injection
SessionDep = Annotated[Session, Depends(get_db)]