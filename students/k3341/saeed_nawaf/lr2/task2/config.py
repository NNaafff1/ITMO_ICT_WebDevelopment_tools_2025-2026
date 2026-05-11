"""
Конфигурация для задачи 2. БД та же, что в Lab 1 (TeamFinder).

Параметры подключения берутся из файла .env. Парсим страницы Wikipedia
о языках программирования и заполняем таблицу `skills` БД из Lab 1.
"""
import os
from pathlib import Path

# Простой загрузчик .env, чтобы не тащить лишнюю зависимость python-dotenv
def _load_env() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "database": os.getenv("DB_NAME", "teamfinder"),
}

DB_DSN = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Wikipedia-страницы языков программирования — стабильные, без anti-bot,
# у каждой есть заголовок и первый абзац-описание.
URLS = [
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://en.wikipedia.org/wiki/JavaScript",
    "https://en.wikipedia.org/wiki/Java_(programming_language)",
    "https://en.wikipedia.org/wiki/C_(programming_language)",
    "https://en.wikipedia.org/wiki/C%2B%2B",
    "https://en.wikipedia.org/wiki/Go_(programming_language)",
    "https://en.wikipedia.org/wiki/Rust_(programming_language)",
    "https://en.wikipedia.org/wiki/TypeScript",
    "https://en.wikipedia.org/wiki/Ruby_(programming_language)",
    "https://en.wikipedia.org/wiki/PHP",
    "https://en.wikipedia.org/wiki/Kotlin_(programming_language)",
    "https://en.wikipedia.org/wiki/Swift_(programming_language)",
]

# Схема `skills` из Lab 1: id, name (UNIQUE, до 100), description (до 300).
# Для безопасности создаём таблицу при необходимости (IF NOT EXISTS).
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS skills (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(300)
);
"""

# UPSERT по name — чтобы повторные запуски не падали с UniqueViolation,
# а обновляли описание (и три парсера могут запускаться подряд).
UPSERT_SQL = """
INSERT INTO skills (name, description)
VALUES (%s, %s)
ON CONFLICT (name) DO UPDATE
SET description = EXCLUDED.description;
"""

# User-Agent — Wikipedia не любит запросы без него и может отвечать 403.
HTTP_HEADERS = {
    "User-Agent": "Lab2-Parser/1.0 (educational project)",
}
