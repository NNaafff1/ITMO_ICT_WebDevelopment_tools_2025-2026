FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# -A celery_app — модуль с инстансом celery_app
# worker — режим воркера (есть ещё beat для периодических задач)
# --loglevel=info — стандартный уровень для контейнеров
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
