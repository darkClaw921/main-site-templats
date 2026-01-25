# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости через uv
RUN uv sync --frozen --no-dev

# Копируем код приложения
COPY . .

# Создаем директорию для загрузок если её нет
RUN mkdir -p app/static/uploads

# Открываем порт
EXPOSE 8000

# Запускаем приложение через uv с поддержкой hot reload
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
