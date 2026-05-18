"""
Celery-приложение для асинхронного парсинга.

Брокер — Redis (хранит очередь задач).
Бэкенд — тоже Redis (хранит статусы и результаты).

Адреса берутся из переменных окружения, которые приходят из docker-compose:
- REDIS_URL=redis://redis:6379/0
"""
import os

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "lab3_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Тяжёлая задача парсинга не должна задерживать другие — короткий visibility timeout
    broker_transport_options={"visibility_timeout": 3600},
    # Результат живёт час — достаточно для опроса клиентом
    result_expires=3600,
)
