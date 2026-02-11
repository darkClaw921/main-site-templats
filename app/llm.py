"""Модуль для работы с LLM и генерации проектов и доработок"""
from typing import Dict, Optional
import httpx
from openai import OpenAI
from app.config import settings


def get_github_repo_info(repo_url: str) -> Optional[str]:
    """Получить информацию о репозитории GitHub"""
    try:
        # Парсинг URL репозитория
        # Поддерживаем форматы: https://github.com/owner/repo или github.com/owner/repo
        repo_url = repo_url.strip()
        if repo_url.startswith("http://") or repo_url.startswith("https://"):
            parts = repo_url.replace("http://", "").replace("https://", "").split("/")
        else:
            parts = repo_url.split("/")
        
        if len(parts) < 3 or parts[0] != "github.com":
            return None
        
        owner = parts[1]
        repo = parts[2].replace(".git", "").split("#")[0].split("?")[0]
        
        # Получение информации через GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url)
            if response.status_code != 200:
                return None
            
            repo_data = response.json()
            
            # Формирование описания репозитория
            description_parts = []
            
            if repo_data.get("description"):
                description_parts.append(f"Описание: {repo_data['description']}")
            
            if repo_data.get("name"):
                description_parts.append(f"\nНазвание репозитория: {repo_data['name']}")
            
            # Попытка получить README отдельно
            readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            readme_response = client.get(readme_url, headers={"Accept": "application/vnd.github.v3+json"})
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if readme_data.get("content"):
                    import base64
                    try:
                        readme_content = base64.b64decode(readme_data["content"]).decode("utf-8")
                        # Ограничиваем размер README
                        readme_content = readme_content[:3000]
                        description_parts.append(f"\nREADME:\n{readme_content}")
                    except Exception:
                        pass
            
            if repo_data.get("language"):
                description_parts.append(f"\nОсновной язык: {repo_data['language']}")
            
            if repo_data.get("topics"):
                description_parts.append(f"\nТемы: {', '.join(repo_data['topics'])}")
            
            if repo_data.get("homepage"):
                description_parts.append(f"\nДомашняя страница: {repo_data['homepage']}")
            
            return "\n".join(description_parts) if description_parts else None
            
    except Exception as e:
        print(f"Ошибка при получении информации о репозитории: {e}")
        return None


def generate_project_with_llm(description: str) -> Dict[str, str]:
    """Генерировать проект через LLM на основе описания"""
    if not settings.openai_key:
        raise ValueError("OPENAI_KEY не настроен в .env")
    
    client = OpenAI(api_key=settings.openai_key)
    
    prompt = f"""Ты помощник для создания описания проекта в портфолио. На основе следующего описания проекта или репозитория, создай структурированное описание проекта.

Описание проекта:
{description}

Верни ответ в формате JSON со следующими полями:
{{
    "title": "Название проекта",
    "industry": "Отрасль проекта",
    "results": ["Результат 1", "Результат 2", "Результат 3"],
    "timeline": "Сроки проекта (например, '3 месяца')",
    "budget": "Бюджет проекта (например, '500 000 руб')",
    "benefits": "Выгода для клиента (2-3 предложения)",
    "tech_stack": {{
        "Frontend": "технологии фронтенда",
        "Backend": "технологии бэкенда",
        "База данных": "технологии БД"
    }}
}}

Важно:
- Название должно быть кратким и понятным
- Отрасль должна быть конкретной (например, "E-commerce", "Финтех", "Образование")
- Результаты должны быть конкретными и измеримыми (3-5 пунктов)
- Сроки и бюджет должны быть реалистичными
- Выгода должна описывать конкретные преимущества для клиента
- Технологический стек должен соответствовать описанию проекта
- Используй только стандартные категории: Frontend, Backend, База данных (можно добавить другие если нужно)
- Верни ТОЛЬКО валидный JSON без дополнительного текста"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты помощник для создания описаний проектов. Всегда отвечаешь только валидным JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Очистка ответа от markdown форматирования если есть
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        import json
        project_data = json.loads(content)
        
        return project_data
        
    except Exception as e:
        raise ValueError(f"Ошибка при генерации проекта через LLM: {str(e)}")


def generate_tweak_with_llm(description: str) -> Dict[str, str]:
    """Генерировать мелкую доработку через LLM на основе описания"""
    if not settings.openai_key:
        raise ValueError("OPENAI_KEY не настроен в .env")

    client = OpenAI(api_key=settings.openai_key)

    prompt = f"""Ты помощник для создания описания мелкой доработки в портфолио IT-компании. На основе следующего описания создай структурированное описание доработки.

Описание:
{description}

Верни ответ в формате JSON со следующими полями:
{{
    "title": "Краткое название доработки (до 80 символов)",
    "description": "Подробное описание что было сделано (2-4 предложения)",
    "category": "категория доработки",
    "project_name": "Название проекта (если понятно из контекста, иначе null)",
    "time_spent": "Примерное время выполнения (например, '2 часа', '1 день')"
}}

Допустимые значения для category:
- "bug_fix" — исправление бага
- "ui" — UI улучшение
- "optimization" — оптимизация производительности
- "feature" — новая небольшая функция
- "refactoring" — рефакторинг кода
- "other" — другое

Важно:
- Название должно быть конкретным и описывать суть доработки
- Описание должно пояснять что именно было сделано и какой эффект
- Категория должна точно соответствовать типу работы
- Время должно быть реалистичным для мелкой доработки
- Верни ТОЛЬКО валидный JSON без дополнительного текста"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты помощник для создания описаний мелких доработок. Всегда отвечаешь только валидным JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        # Очистка ответа от markdown форматирования если есть
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        import json
        tweak_data = json.loads(content)

        return tweak_data

    except Exception as e:
        raise ValueError(f"Ошибка при генерации доработки через LLM: {str(e)}")
