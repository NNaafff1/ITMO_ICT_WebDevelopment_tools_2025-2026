# Docker и docker-compose

## Подзадача 1 из ТЗ

Упаковать в Docker три приложения: FastAPI из Lab 1, базу данных и
парсер из Lab 2. Использованы три отдельных Dockerfile-а и общий
`docker-compose.yaml`.

## Dockerfile основного API

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY alembic.ini ./
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

**Что важно:**

- `python:3.12-slim` — компромисс между размером и удобством. Образ
  ~120 МБ, есть apt для системных пакетов при необходимости.
- `PYTHONUNBUFFERED=1` — stdout/stderr не буферизуются. Иначе при
  падении контейнера логи могут не успеть записаться, и причину
  падения будет не видно.
- `PYTHONDONTWRITEBYTECODE=1` — не создаём `__pycache__`, экономит
  место на слое.
- Сначала `COPY requirements.txt` и `pip install`, потом `COPY src/`.
  Docker кеширует слои; пока `requirements.txt` не менялся, тяжёлый
  шаг с установкой зависимостей не пересобирается при правках в `src/`.
- `--proxy-headers` — если позже добавим nginx/traefik, uvicorn будет
  доверять заголовкам `X-Forwarded-*`.

## Dockerfile парсера и воркера

Структурно те же. Парсер отличается только портом (`8001`) и
командой запуска (`uvicorn src.main:app`). Воркер запускает не
uvicorn, а Celery:

```dockerfile
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
```

## docker-compose.yaml

Пять сервисов: `db`, `redis`, `api`, `parser`, `worker`.

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME:-teamfinder}
      ...
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-teamfinder}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      ...

  api:
    build: ./api
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://...@db:5432/teamfinder
      PARSER_URL: http://parser:8001
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
      parser: { condition: service_started }

  parser:
    build: ./parser_service
    ports: ["8001:8001"]

  worker:
    build: ./worker
    environment:
      DATABASE_URL: postgresql://...@db:5432/teamfinder
      REDIS_URL: redis://redis:6379/0
      PARSER_URL: http://parser:8001
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }

volumes:
  postgres_data:
```

**Что важно:**

- **Healthcheck-и для db и redis.** Если api или worker стартанут
  раньше БД, они упадут с `Connection refused`. `condition:
  service_healthy` в `depends_on` заставляет compose дождаться, пока
  pg_isready и redis-cli ping вернут OK.
- **Сервисы видят друг друга по имени.** Внутри сети compose имя
  сервиса работает как DNS-имя. `parser` доступен из api как
  `http://parser:8001`, redis — как `redis://redis:6379/0`. Никаких
  IP-адресов не нужно.
- **Переменные окружения через `.env`.** Никаких секретов в
  репозитории. `.env.example` закоммичен, `.env` — в `.gitignore`.
  Значения по умолчанию через `${VAR:-default}` нужны на случай если
  кто-то забыл создать `.env`.
- **Именованный volume `postgres_data`.** Данные БД переживают
  `docker compose down`. Очистить можно через `docker compose down -v`.
- **`build:` вместо `image:`.** Образы собираются локально из
  Dockerfile-ов. Это нормально для учебной лабы; в продакшене образы
  обычно собирают в CI и пушат в registry, а compose ссылается на
  готовый тег.

## Команды

```bash
docker compose up --build         # сборка и запуск всех 5 сервисов
docker compose up --build -d      # то же, но в фоне
docker compose logs -f api        # хвост логов одного сервиса
docker compose down               # остановка, данные БД сохраняются
docker compose down -v            # остановка + удаление volume с БД
docker compose ps                 # статус сервисов
docker compose up --scale worker=3  # три воркера на одну очередь
```
