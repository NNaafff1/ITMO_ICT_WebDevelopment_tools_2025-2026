# Лабораторная работа 3 — Saeed Nawaf, k3341

Упаковка FastAPI в Docker, сервис-парсер по HTTP, очередь задач Celery + Redis.

## Быстрый старт

```bash
# 1. Скопировать переменные окружения
cp .env.example .env
# (отредактируйте SECRET_KEY на случайную строку, опционально)

# 2. Собрать и запустить пять сервисов
docker compose up --build
```

Откроется пять контейнеров: `db` (PostgreSQL), `redis`, `api`
(http://localhost:8000), `parser` (http://localhost:8001), `worker`
(Celery в фоне).

Документация Swagger: http://localhost:8000/docs

## Что внутри

- `api/` — основное FastAPI приложение (Lab 1 + новый роутер `/parser`)
- `parser_service/` — отдельное FastAPI-приложение для парсинга (как
  требует ТЗ — «парсер, запущенный в отдельном контейнере»)
- `worker/` — Celery-воркер для фоновых задач
- `docker-compose.yaml` — оркестратор пяти сервисов
- `docs/` — MkDocs документация (отчёт по лабе)

## Полный отчёт

Все детали в `docs/`. Локальный просмотр:

```bash
pip install mkdocs mkdocs-material
mkdocs serve     # http://127.0.0.1:8000
```

После push в ветку `lab3` GitHub Actions автоматически
опубликует docs на
`https://nnaafff1.github.io/ITMO_ICT_WebDevelopment_tools_2025-2026/lr3/`.

## Проверка работы

```bash
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@e.com","password":"demopass1","full_name":"Demo"}'

# Логин — сохранить токен
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -F "username=demo" -F "password=demopass1" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Синхронный парсинг
curl -X POST http://localhost:8000/parser/parse \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Python_(programming_language)"}'

# Асинхронный парсинг
curl -X POST http://localhost:8000/parser/parse-async \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Rust_(programming_language)"}'

# Опрос статуса (взять task_id из ответа выше)
curl http://localhost:8000/parser/tasks/<TASK_ID>
```

Подробные инструкции — в [docs/usage.md](docs/usage.md).

## Скриншоты

В `docs/screenshots/` лежат **заглушки** (серые PNG). Перед сдачей
замените их на реальные скриншоты работы системы — список
обязательных в [docs/screenshots.md](docs/screenshots.md).
