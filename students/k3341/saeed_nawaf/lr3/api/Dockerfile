FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Системные пакеты для psycopg2 (postgres) — нужны только на этапе сборки
# wheel'а нет под slim, поэтому компилируем из исходников.
# Можно было взять psycopg2-binary, но мы и так его используем — header'ы
# для C-расширений не нужны.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY alembic.ini ./
COPY migrations/ ./migrations/

EXPOSE 8000

# --proxy-headers важно если будем за реверс-прокси (nginx/traefik) —
# uvicorn будет верить заголовкам X-Forwarded-* и отдавать правильные URL.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
