# Задача 2 — Параллельный парсинг + сохранение в БД

## Описание

Парсятся 12 страниц Wikipedia о популярных языках программирования.
С каждой страницы извлекается:

- **`name`** — название языка из `<h1 id="firstHeading">`;
- **`description`** — первый содержательный абзац статьи (до 300 символов).

Данные сохраняются в таблицу `skills` БД `teamfinder` из лабораторной
работы №1.

Это естественно ложится на схему Lab 1: пользователи платформы
TeamFinder привязывают к своим профилям навыки через таблицу
`user_skills(user_id, skill_id, level)`.

**Подключение к БД во всех трёх вариантах асинхронное** через
`psycopg`, как требует задание. Для UPSERT используется
`ON CONFLICT (name) DO UPDATE`, поэтому повторные запуски не падают
по уникальному ограничению, а обновляют запись.

## Схема таблицы

```sql
CREATE TABLE skills (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(300)
);
```

SQLAlchemy-модель (`task2/models.py`) — для документирования схемы:

```python
class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=True)
```

## Парсер Wikipedia (общий код)

Файл `task2/parser_common.py` — функция `parse_wiki_page(html)`,
которая возвращает кортеж `(name, description)`. Используется во
всех трёх реализациях:

```python
def parse_wiki_page(html):
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.select_one("h1#firstHeading")
    raw_title = h1.get_text(strip=True)
    name = re.sub(r"\s*\([^)]*\)\s*", "", raw_title).strip()[:100]

    content = soup.select_one("div.mw-parser-output")
    description = ""
    for p in content.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 50:
            description = text
            break
    description = re.sub(r"\[\d+\]", "", description)[:300]
    return name, description
```

## Реализация 1 — threading

Файл: `task2/scrape_threading.py`

Каждый поток через `requests` загружает свою страницу. GIL
отпускается на время сетевого ожидания, поэтому потоки реально
работают параллельно. Результаты собираются в `queue.Queue`
(потокобезопасная). После завершения всех потоков основной поток
запускает асинхронную запись в БД.

```python
def parse_and_save(url, results):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    name, desc = parse_wiki_page(resp.text)
    results.put((url, name, desc))

threads = [threading.Thread(target=parse_and_save, args=(u, results))
           for u in URLS]
for t in threads: t.start()
for t in threads: t.join()

# Асинхронное сохранение через psycopg
asyncio.run(save_all(rows))
```

**Особенность:** один процесс, потоки переключаются на сетевом
ожидании. Хорошо подходит для I/O-bound задач.

## Реализация 2 — multiprocessing

Файл: `task2/scrape_multiprocessing.py`

Каждый процесс независимо качает и парсит свою страницу. Для I/O
это избыточно (накладные расходы на запуск процессов превышают
выигрыш), но задание требует этот вариант для сравнения.

```python
with mp.Pool(processes=4) as pool:
    results = pool.map(parse_and_save, URLS)
asyncio.run(save_all(results))
```

**Особенность:** изоляция процессов даёт настоящий параллелизм, но
форк процессов, сериализация HTML через pickle и связанные
накладные расходы делают этот подход самым медленным для данной
задачи.

## Реализация 3 — asyncio + aiohttp

Файл: `task2/scrape_async.py`

Самый эффективный для I/O вариант. Все 12 запросов запускаются
одновременно в `asyncio.gather`. Подключение к БД — через пул
`AsyncConnectionPool`.

```python
async def parse_and_save(session, pool, url):
    async with session.get(url, headers=HEADERS) as resp:
        html = await resp.text()
    name, desc = parse_wiki_page(html)
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(UPSERT_SQL, (name, desc))
        await conn.commit()

async with AsyncConnectionPool(DB_DSN, max_size=5) as pool:
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *(parse_and_save(session, pool, url) for url in URLS)
        )
```

**Особенность:** один поток, один процесс, десятки параллельных
корутин. Никаких накладных расходов на потоки/процессы.

## Результаты

Запуск через `task2/benchmark.py` — все три парсера по очереди,
итоговая таблица времени.

| Подход | Время выполнения |
|---|---:|
| threading | 6.55 сек |
| multiprocessing | 4.24 сек |
| async | 0.88 сек |

## Содержимое БД после парсинга

После прогона любой из трёх программ:

```
SELECT id, name, LEFT(description, 60) || '...' AS description FROM skills ORDER BY id;
```

```
 id |    name    |                          description
----+------------+----------------------------------------------------------
  1 | Python     | Python is a high-level, general-purpose programming...
  2 | JavaScript | JavaScript, often abbreviated as JS, is a programmin...
  3 | Java       | Java is a high-level, class-based, object-oriented...
  4 | C          | C is a general-purpose programming language. It was...
  5 | C++        | C++ is a high-level, general-purpose programming...
  ...
```

## Анализ результатов

**threading** работает быстро: пока один поток ждёт ответ от
Wikipedia, остальные уже отправили свои запросы. GIL не мешает,
потому что в момент сетевого ожидания он отпущен. Это
классический сценарий, где threading блестит.

**multiprocessing** в этой задаче проигрывает: запуск процессов,
сериализация HTML между процессами и накладные расходы превышают
выигрыш от параллелизма. Для I/O-bound задач он почти всегда
избыточен.

**async** обычно быстрее всех. Один поток обрабатывает все 12
запросов в `asyncio.gather` одновременно — это самый эффективный
подход для массовых I/O-операций. При 100+ URL разрыв с threading
станет ещё больше.

### Вывод по задаче 2

Для I/O-bound задач (сеть, диск) лучшим выбором является `asyncio`;
`threading` тоже хорош и проще в реализации; `multiprocessing`
почти всегда избыточен.

Дальше — [Итоговые выводы](conclusion.md).
