# Скриншоты

Иллюстрации работы системы.

## Запущенные сервисы

docker compose ps — пять сервисов в статусе running.

![Compose status](screenshots/compose_ps.png)

## Swagger UI основного API

http://localhost:8000/docs — видны все группы эндпоинтов,
включая раздел Parser с тремя маршрутами.

![API Swagger](screenshots/api_swagger.png)

## Синхронный парсинг

POST /parser/parse через Swagger UI или curl. В ответе видно
созданный skill.

![Sync parse](screenshots/sync_parse.png)

## Логи воркера

docker compose logs -f worker — Celery принимает и завершает задачу.

![Worker logs](screenshots/worker_logs.png)

## Содержимое таблицы skills

\`\`\`bash
docker compose exec db psql -U postgres -d teamfinder \
  -c "SELECT id, name, LEFT(description, 60) || '...' AS description FROM skills ORDER BY id;"
\`\`\`

Записи появились после успешного парсинга.

![DB skills](screenshots/db_skills.png)