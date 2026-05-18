"""
Сервис-парсер. Отдельное FastAPI приложение, запускается в собственном
контейнере и предоставляет один эндпоинт POST /parse.

Принимает URL Wikipedia-страницы языка программирования, скачивает HTML,
извлекает name и description (как в Lab 2) и возвращает результат JSON.

Парсер НЕ пишет в базу данных — он только парсит. За сохранение в БД
отвечает основное API (sync-эндпоинт) или Celery-воркер (async).
Это даёт чистое разделение ответственности между сервисами.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from src.parser import fetch_and_parse

app = FastAPI(
    title="TeamFinder Parser Service",
    description="Микросервис для парсинга Wikipedia-страниц языков программирования",
    version="1.0.0",
)


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    url: str
    name: str
    description: str


@app.get("/", tags=["Health"])
def health() -> dict:
    return {"status": "ok", "service": "parser"}


@app.post("/parse", response_model=ParseResponse, tags=["Parser"])
def parse(request: ParseRequest) -> ParseResponse:
    """Скачивает страницу, парсит, возвращает (name, description)."""
    try:
        name, description = fetch_and_parse(str(request.url))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parse failed: {exc}")
    return ParseResponse(url=str(request.url), name=name, description=description)
