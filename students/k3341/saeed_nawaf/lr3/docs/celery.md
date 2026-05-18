# Celery и Redis

## Подзадача 3 из ТЗ

Реализовать вызов парсера из FastAPI через очередь: клиент шлёт URL,
задача попадает в Redis, Celery-воркер обрабатывает её в фоне, клиент
опрашивает статус.

## Зачем это нужно

Синхронный `/parser/parse` ждёт ответа от Wikipedia, и если страниц
много или сеть медленная, клиент висит на запросе. Очередь даёт
другую модель:

1. Клиент шлёт URL и сразу получает `task_id` (HTTP 202 Accepted).
2. Парсинг происходит в воркере в фоне.
3. Клиент в удобный момент опрашивает статус.

Это **не делает парсинг быстрее** — это перекладывает ожидание с
клиента на воркер. Зато:

- API остаётся отзывчивым: воркер падает или тормозит — API всё равно
  принимает новые запросы.
- Воркеры можно масштабировать независимо (`--scale worker=N`).
- Можно ретраить неудачные задачи (у нас `max_retries=3`).
- Можно ставить много задач одной транзакцией — батч-парсинг сотен URL.

## Целевой стек

| Компонент | Роль | Контейнер |
|---|---|---|
| Celery 5.4 | Фреймворк задач | `worker` |
| Redis 7 | Брокер очереди + бэкенд результатов | `redis` |
| `celery` (клиент) | Постановка задач из api | внутри `api` |

## celery_app.py

```python
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
    broker_transport_options={"visibility_timeout": 3600},
    result_expires=3600,
)
```

**Что важно:**

- **Один Redis служит и брокером, и бэкендом.** Брокер хранит очередь
  задач (что выполнить), бэкенд — результаты (что получилось). Для
  учебной лабы один инстанс справляется с обеими ролями.
- **JSON-сериализация, не pickle.** Pickle быстрее, но открывает
  выполнение произвольного кода при десериализации. JSON безопаснее
  и совместим между языками.
- **`result_expires=3600`.** Результаты живут в Redis час, потом
  чистятся. Иначе Redis распухнет.

## tasks.py

```python
@celery_app.task(name="parse_url_task", bind=True, max_retries=3, default_retry_delay=10)
def parse_url_task(self, url: str) -> dict:
    try:
        resp = requests.post(f"{PARSER_URL}/parse", json={"url": url}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        name = data["name"]
        description = data["description"]
    except requests.RequestException as exc:
        raise self.retry(exc=exc)

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

    return {"url": url, "name": name, "description": description, "action": action}
```

**Что важно:**

- **`bind=True`** даёт доступ к `self` (контексту задачи) и позволяет
  вызывать `self.retry()`.
- **`max_retries=3, default_retry_delay=10`** — если парсер
  недоступен, повторяем три раза с интервалом 10 секунд.
- **Воркер использует тот же сервис-парсер, что и sync-эндпоинт.**
  Единственный источник истины для логики парсинга. Если завтра
  понадобится переехать на другую библиотеку, меняем только
  `parser_service`.
- **Возвращаемое значение — это и есть результат, который заберёт
  клиент** через `GET /parser/tasks/{id}`.

## Эндпоинты в API

### Постановка задачи

```python
@router.post("/parse-async", response_model=ParseAsyncResponse, status_code=202)
def parse_async(request: ParseRequest, current_user=Depends(get_current_user)):
    async_result = celery_client.send_task("parse_url_task", args=[str(request.url)])
    return ParseAsyncResponse(
        task_id=async_result.id,
        status="queued",
        message="Task accepted. Poll /parser/tasks/{task_id} for status.",
    )
```

**Важная деталь:** `celery_client.send_task("parse_url_task", ...)`
работает в API даже без импорта самой функции задачи. Достаточно
знать имя. Это разделяет код API и воркера — у них могут даже быть
разные версии Python, лишь бы они говорили с одним Redis.

### Опрос статуса

```python
@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_client)
    response = {"task_id": task_id, "status": result.status, "result": None}
    if result.successful():
        response["result"] = result.result
    elif result.failed():
        response["result"] = {"error": str(result.result)}
    return response
```

**Статусы Celery:**

| Статус | Значение |
|---|---|
| `PENDING` | Задача ещё в очереди или ID не существует (Celery не отличает) |
| `STARTED` | Воркер взял задачу в работу (нужен `task_track_started=True`) |
| `SUCCESS` | Готово, в `result` лежит возвращённый dict |
| `FAILURE` | Упало, в `result` лежит исключение |
| `RETRY` | Ретраится |

## Сервисы в compose

Добавлены два новых:

```yaml
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  worker:
    build: ./worker
    environment:
      DATABASE_URL: postgresql://...@db:5432/teamfinder
      REDIS_URL: redis://redis:6379/0
      PARSER_URL: http://parser:8001
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
```

В `api` тоже добавлены `REDIS_URL` и `PARSER_URL`. Сам `api` теперь
зависит от `redis: service_healthy` — иначе клиент Celery упадёт при
старте.
