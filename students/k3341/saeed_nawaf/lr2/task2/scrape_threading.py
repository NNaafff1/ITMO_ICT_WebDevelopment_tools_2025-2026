"""
Задача 2 — параллельный парсинг с использованием threading.

Загрузка HTML — это I/O-bound операция, для неё threading работает хорошо:
пока поток ждёт ответа от сервера, GIL отдаётся другим потокам.
Каждый поток парсит свою страницу и кладёт результат в потокобезопасную
очередь. После завершения всех потоков основной поток асинхронно (через
psycopg AsyncConnection) сохраняет данные в таблицу `skills` БД Lab 1.
"""
import asyncio
import sys
import threading
import time
from queue import Queue

import psycopg
import requests

from config import CREATE_TABLE_SQL, DB_DSN, HTTP_HEADERS, UPSERT_SQL, URLS
from parser_common import parse_wiki_page

# На Windows psycopg не работает с дефолтным ProactorEventLoop —
# переключаемся на SelectorEventLoop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def parse_and_save(url: str, results: Queue) -> None:
    """Загружает страницу, парсит, кладёт (url, name, description) в очередь."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        resp.raise_for_status()
        name, description = parse_wiki_page(resp.text)
        print(f"[threading] {url} -> {name!r}")
        results.put((url, name, description))
    except Exception as exc:
        print(f"[threading] Ошибка при обработке {url}: {exc}")


async def save_all(rows: list[tuple[str, str, str]]) -> None:
    """Асинхронно записывает все собранные навыки в таблицу skills."""
    async with await psycopg.AsyncConnection.connect(DB_DSN) as conn:
        async with conn.cursor() as cur:
            await cur.execute(CREATE_TABLE_SQL)
            await cur.executemany(
                UPSERT_SQL,
                [(name, description) for _, name, description in rows],
            )
        await conn.commit()


def run() -> float:
    """Выполняет парсинг и возвращает время работы. Используется в benchmark.py."""
    results: Queue = Queue()
    threads = []

    t0 = time.perf_counter()
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url, results))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    rows = []
    while not results.empty():
        rows.append(results.get())

    asyncio.run(save_all(rows))
    elapsed = time.perf_counter() - t0
    print(f"[threading] Готово. Сохранено навыков: {len(rows)}. Время: {elapsed:.2f} сек")
    return elapsed


def main() -> None:
    print(f"[threading] Парсим {len(URLS)} страниц Wikipedia в потоках")
    run()


if __name__ == "__main__":
    main()
