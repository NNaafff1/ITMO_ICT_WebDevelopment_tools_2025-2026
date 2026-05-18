"""
Эндпоинты для интеграции парсера в основное API.

Три маршрута:

1. POST /parser/parse — синхронный вызов парсера.
   Принимает URL, делает HTTP-запрос к сервису-парсеру (отдельный
   контейнер), сохраняет результат в БД, возвращает ответ клиенту.

2. POST /parser/parse-async — асинхронный вызов через Celery.
   Принимает URL, ставит задачу в очередь Redis, сразу возвращает
   task_id. Клиент опрашивает статус через GET /parser/tasks/{id}.

3. GET /parser/tasks/{task_id} — статус и результат фоновой задачи.
"""
import os
from typing import Any

import requests
from celery import Celery
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from src import crud
from src.auth import get_current_user
from src.database import get_db
from src.schemas import SkillResponse

router = APIRouter(prefix="/parser", tags=["Parser"])

# Адрес сервиса-парсера — внутри docker-compose это http://parser:8001
PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")
PARSER_TIMEOUT = 30

# Тот же Celery-инстанс, что и в воркере — нужен только для отправки
# задач и получения результатов, никакие задачи здесь не регистрируются.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_client = Celery("lab3_client", broker=REDIS_URL, backend=REDIS_URL)


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseAsyncResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any | None = None


@router.post("/parse", response_model=SkillResponse, status_code=201)
def parse_sync(
    request: ParseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Синхронный парсинг: вызывает сервис-парсер и сразу сохраняет в БД.

    Авторизация обязательна — анонимы не должны нагружать парсер.
    Возвращает созданный (или обновлённый) skill.
    """
    try:
        resp = requests.post(
            f"{PARSER_URL}/parse",
            json={"url": str(request.url)},
            timeout=PARSER_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Parser service unavailable: {exc}")

    name = data["name"]
    description = data["description"]

    # UPSERT по name — повторный парсинг той же страницы не падает,
    # а обновляет описание.
    from src.models import Skill
    from src.schemas import SkillCreate

    existing = db.query(Skill).filter(Skill.name == name).first()
    if existing:
        existing.description = description
        db.commit()
        db.refresh(existing)
        return existing

    return crud.create_skill(db, SkillCreate(name=name, description=description))


@router.post("/parse-async", response_model=ParseAsyncResponse, status_code=202)
def parse_async(
    request: ParseRequest,
    current_user=Depends(get_current_user),
):
    """Асинхронный парсинг: ставит задачу в Celery, возвращает task_id.

    202 Accepted — стандартный код для «принял, выполняю в фоне».
    Клиент потом опрашивает GET /parser/tasks/{task_id}.
    """
    async_result = celery_client.send_task("parse_url_task", args=[str(request.url)])
    return ParseAsyncResponse(
        task_id=async_result.id,
        status="queued",
        message="Task accepted. Poll /parser/tasks/{task_id} for status.",
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """Возвращает статус и результат Celery-задачи.

    Статусы Celery: PENDING (не найдена или ещё в очереди), STARTED,
    SUCCESS, FAILURE, RETRY. Результат доступен только после SUCCESS.
    """
    result = AsyncResult(task_id, app=celery_client)
    response: dict[str, Any] = {"task_id": task_id, "status": result.status, "result": None}
    if result.successful():
        response["result"] = result.result
    elif result.failed():
        response["result"] = {"error": str(result.result)}
    return response
