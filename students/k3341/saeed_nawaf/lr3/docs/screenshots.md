# Скриншоты

Иллюстрации работы системы. Скриншоты нужно положить в
`docs/screenshots/` под этими именами:

## Запущенные сервисы

`docker compose ps` — пять сервисов в статусе `running`.

![Compose status](screenshots/compose_ps.png)

## Swagger UI основного API

`http://localhost:8000/docs` — видны все группы эндпоинтов,
включая раздел **Parser** с тремя маршрутами.

![API Swagger](screenshots/api_swagger.png)

## Swagger UI сервиса-парсера

`http://localhost:8001/docs` — единственный содержательный эндпоинт
`POST /parse`.

![Parser Swagger](screenshots/parser_swagger.png)

## Синхронный парсинг

`POST /parser/parse` через Swagger UI или curl. В ответе видно
созданный skill.

![Sync parse](screenshots/sync_parse.png)

## Асинхронный парсинг — постановка задачи

`POST /parser/parse-async` — ответ с `task_id` и статусом `queued`.

![Async parse queued](screenshots/async_queued.png)

## Опрос статуса задачи

`GET /parser/tasks/{id}` — задача в статусе `SUCCESS` и результат.

![Task status](screenshots/task_status.png)

## Логи воркера

`docker compose logs -f worker` — Celery принимает и завершает задачу.

![Worker logs](screenshots/worker_logs.png)

## Содержимое таблицы skills

```bash
docker compose exec db psql -U postgres -d teamfinder \
  -c "SELECT id, name, LEFT(description, 60) FROM skills ORDER BY id;"
```

Записи появились после успешного парсинга.

![DB skills](screenshots/db_skills.png)
