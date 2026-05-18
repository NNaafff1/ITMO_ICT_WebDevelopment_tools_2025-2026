"""
Celery-задачи.

`parse_url_task` — основная задача:
1. Дёргает сервис-парсер по HTTP (тот же, что использует sync-эндпоинт).
   Это даёт единственный источник истины для логики парсинга.
2. Записывает результат в таблицу skills через SQLAlchemy с UPSERT-поведением
   (если name уже есть — обновляем description).

Воркер ходит в БД напрямую — это нормально для фоновых задач. Альтернатива —
звать API изнутри воркера, но это лишний хоп и циркулярная зависимость.
"""
import os

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from celery_app import celery_app
from models import Skill, Base

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/teamfinder")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_tables() -> None:
    """На случай если воркер стартанул раньше, чем API создало таблицы."""
    Base.metadata.create_all(bind=engine)


@celery_app.task(name="parse_url_task", bind=True, max_retries=3, default_retry_delay=10)
def parse_url_task(self, url: str) -> dict:
    """Парсит URL через сервис-парсер и сохраняет skill в БД.

    Возвращает dict с результатом, который Celery сохранит в Redis
    как result. Клиент сможет его забрать через GET /tasks/{task_id}.
    """
    try:
        resp = requests.post(
            f"{PARSER_URL}/parse",
            json={"url": url},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        name = data["name"]
        description = data["description"]
    except requests.RequestException as exc:
        # Сетевые ошибки — ретраим (Wikipedia могла моргнуть)
        raise self.retry(exc=exc)

    _ensure_tables()
    db = SessionLocal()
    try:
        existing = db.query(Skill).filter(Skill.name == name).first()
        if existing:
            existing.description = description
            action = "updated"
        else:
            db.add(Skill(name=name, description=description))
            action = "created"
        db.commit()
    finally:
        db.close()

    return {
        "url": url,
        "name": name,
        "description": description,
        "action": action,
    }
