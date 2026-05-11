"""
Задача 2 — параллельный парсинг с использованием multiprocessing.

Каждый процесс независимо загружает и парсит страницу. Для I/O-bound
задачи это избыточно (накладные расходы на запуск процессов превышают
выигрыш), но задание требует именно этот вариант для сравнения с
threading и async.

После сбора результатов основной процесс асинхронно (psycopg) сохраняет
их в таблицу `skills` БД Lab 1.
"""
import asyncio
import multiprocessing as mp
import sys
import time

import psycopg
import requests

from config import CREATE_TABLE_SQL, DB_DSN, HTTP_HEADERS, UPSERT_SQL, URLS
from parser_common import parse_wiki_page

# На Windows psycopg не работает с дефолтным ProactorEventLoop —
# переключаемся на SelectorEventLoop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def parse_and_save(url: str) -> tuple[str, str, str] | None:
    """Скачивает и парсит страницу. Возвращает кортеж для последующей записи."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        resp.raise_for_status()
        name, description = parse_wiki_page(resp.text)
        print(f"[multiprocessing] {url} -> {name!r}")
        return (url, name, description)
    except Exception as exc:
        print(f"[multiprocessing] Ошибка при обработке {url}: {exc}")
        return None


async def save_all(rows: list[tuple[str, str, str]]) -> None:
    async with await psycopg.AsyncConnection.connect(DB_DSN) as conn:
        async with conn.cursor() as cur:
            await cur.execute(CREATE_TABLE_SQL)
            await cur.executemany(
                UPSERT_SQL,
                [(name, description) for _, name, description in rows],
            )
        await conn.commit()


def run() -> float:
    t0 = time.perf_counter()
    with mp.Pool(processes=min(len(URLS), 4)) as pool:
        results = pool.map(parse_and_save, URLS)
    rows = [r for r in results if r is not None]
    asyncio.run(save_all(rows))
    elapsed = time.perf_counter() - t0
    print(f"[multiprocessing] Готово. Сохранено навыков: {len(rows)}. Время: {elapsed:.2f} сек")
    return elapsed


def main() -> None:
    print(f"[multiprocessing] Парсим {len(URLS)} страниц Wikipedia в процессах")
    run()


if __name__ == "__main__":
    main()
