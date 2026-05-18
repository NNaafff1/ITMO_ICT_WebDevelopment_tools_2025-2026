# Запуск

## Предусловия

- Docker и docker compose v2 (входит в Docker Desktop)
- Свободные порты `5432`, `6379`, `8000`, `8001`
- ~500 МБ свободного места под образы

## Шаг 1 — переменные окружения

```bash
cd students/k3341/saeed_nawaf/lr3
cp .env.example .env
# Откройте .env и поменяйте SECRET_KEY на случайную строку:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Шаг 2 — сборка и запуск

```bash
docker compose up --build
```

Первая сборка займёт несколько минут (тянет три python-образа и
ставит зависимости). Дальше будет быстро благодаря Docker-кешу.

Ожидаемый вывод (фрагменты):

```
db-1       | LOG:  database system is ready to accept connections
redis-1    | Ready to accept connections tcp
parser-1   | INFO: Uvicorn running on http://0.0.0.0:8001
api-1      | INFO: Application startup complete.
api-1      | INFO: Uvicorn running on http://0.0.0.0:8000
worker-1   | celery@... ready.
```

## Шаг 3 — проверка

### Health-чек

```bash
curl http://localhost:8000/
# {"status":"ok","message":"Team Finder API (Lab 3) is running"}

curl http://localhost:8001/
# {"status":"ok","service":"parser"}
```

### Регистрация и логин

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@e.com","password":"demopass1","full_name":"Demo User"}'

TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -F "username=demo" -F "password=demopass1" | jq -r .access_token)
echo $TOKEN
```

### Синхронный парсинг

```bash
curl -X POST http://localhost:8000/parser/parse \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Python_(programming_language)"}'
```

Ожидаемый ответ:
```json
{
  "id": 1,
  "name": "Python",
  "description": "Python is a high-level, general-purpose programming language..."
}
```

### Асинхронный парсинг

```bash
TASK_ID=$(curl -s -X POST http://localhost:8000/parser/parse-async \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Rust_(programming_language)"}' \
  | jq -r .task_id)
echo $TASK_ID

# Сразу — задача в очереди
curl http://localhost:8000/parser/tasks/$TASK_ID
# {"task_id":"...","status":"PENDING","result":null}

# Через пару секунд
curl http://localhost:8000/parser/tasks/$TASK_ID
# {"task_id":"...","status":"SUCCESS","result":{"url":"...","name":"Rust","description":"...","action":"created"}}
```

### Проверка в БД

```bash
docker compose exec db psql -U postgres -d teamfinder \
  -c "SELECT id, name, LEFT(description, 60) FROM skills ORDER BY id;"
```

## Логи отдельных сервисов

```bash
docker compose logs -f api       # API
docker compose logs -f parser    # парсер
docker compose logs -f worker    # воркер Celery
docker compose logs -f redis     # очередь
```

В логах воркера хорошо видно, как он принимает задачу и завершает её:

```
worker-1  | Received task: parse_url_task[abc-123]
worker-1  | Task parse_url_task[abc-123] succeeded in 0.83s: {'url': '...', 'name': 'Rust', ...}
```

## Свагер UI

- Основное API:  http://localhost:8000/docs
- Сервис-парсер: http://localhost:8001/docs

## Локальный просмотр документации

```bash
pip install mkdocs mkdocs-material
mkdocs serve     # http://127.0.0.1:8000
```

(если 8000 занят API — `mkdocs serve -a 127.0.0.1:8888`)

## Остановка

```bash
docker compose down              # сохраняет данные БД
docker compose down -v           # удаляет volume — чистый старт в следующий раз
```
