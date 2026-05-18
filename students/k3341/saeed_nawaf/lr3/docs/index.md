# Лабораторная работа 3

# Упаковка FastAPI приложения в Docker, источники данных и очереди

**Дата:** Май 2026

---

## Цель работы

Научиться упаковывать FastAPI-приложение в Docker, интегрировать парсер
данных с базой данных и вызывать парсер двумя способами: синхронно
через HTTP и асинхронно через очередь задач Celery + Redis.

## Задание

1. Упаковать FastAPI-приложение из Lab 1, базу данных PostgreSQL и
   парсер из Lab 2 в Docker. Парсер реализован как **отдельный
   FastAPI-сервис в своём контейнере** и принимает запросы по HTTP.
2. Добавить в основное API эндпоинт, который принимает URL от клиента,
   обращается к сервису-парсеру (в другом контейнере) и возвращает
   результат.
3. Добавить эндпоинт асинхронного вызова парсера через Celery + Redis,
   эндпоинт опроса статуса задачи и Celery-воркер в отдельном
   контейнере.

## Структура проекта

```
lr3/
├── docker-compose.yaml          # пять сервисов: db, redis, api, parser, worker
├── .env.example                 # шаблон переменных окружения
├── mkdocs.yml                   # документация
├── api/                         # основное FastAPI приложение (Lab 1 + parser router)
│   ├── src/
│   │   ├── main.py              # подключает все роутеры, включая parser
│   │   ├── routers/parser.py    # /parser/parse, /parser/parse-async, /parser/tasks/{id}
│   │   └── ...                  # auth, users, projects, skills, team_requests (Lab 1)
│   ├── Dockerfile
│   └── requirements.txt
├── parser_service/              # сервис-парсер
│   ├── src/
│   │   ├── main.py              # POST /parse
│   │   └── parser.py            # перенос из Lab 2: BeautifulSoup + requests
│   ├── Dockerfile
│   └── requirements.txt
├── worker/                      # Celery worker
│   ├── celery_app.py
│   ├── tasks.py                 # parse_url_task
│   ├── models.py
│   ├── Dockerfile
│   └── requirements.txt
└── docs/                        # этот сайт (MkDocs)
```

## Содержание отчёта

1. [Архитектура](architecture.md) — диаграмма сервисов и взаимодействий
2. [Docker и compose](docker.md) — Dockerfile-ы, оркестрация, healthcheck-и
3. [Сервис-парсер](parser_service.md) — отдельное FastAPI-приложение
4. [Celery и Redis](celery.md) — очередь, воркер, опрос статуса
5. [Запуск](usage.md) — пошаговая инструкция и примеры curl
6. [Скриншоты](screenshots.md) — рабочая система
7. [Выводы](conclusion.md)
