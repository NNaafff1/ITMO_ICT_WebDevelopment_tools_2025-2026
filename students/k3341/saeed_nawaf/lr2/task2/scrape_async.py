"""
Задача 2 — параллельный парсинг с использованием asyncio + aiohttp.

Самый эффективный для I/O-bound нагрузки вариант: пока одна корутина
ждёт ответа от сервера, другие уже работают. Загрузка страниц
параллельная, запись в БД — через асинхронные подключения psycopg.
"""
import asyncio
import sys
import time

import aiohttp
import psycopg
from psycopg_pool import AsyncConnectionPool

from config import CREATE_TABLE_SQL, DB_DSN, HTTP_HEADERS, UPSERT_SQL, URLS
from parser_common import parse_wiki_page

# На Windows psycopg не работает с дефолтным ProactorEventLoop —
# переключаемся на SelectorEventLoop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def parse_and_save(
    session: aiohttp.ClientSession,
    pool: AsyncConnectionPool,
    url: str,
) -> None:
    """Скачивает, парсит и сохраняет одну страницу — полностью асинхронно."""
    try:
        async with session.get(
            url,
            headers=HTTP_HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            resp.raise_for_status()
            html = await resp.text()

        name, description = parse_wiki_page(html)
        print(f"[async] {url} -> {name!r}")

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(UPSERT_SQL, (name, description))
            await conn.commit()
    except Exception as exc:
        print(f"[async] Ошибка при обработке {url}: {exc}")


async def _run_async() -> None:
    # Создаём таблицу один раз через обычное подключение
    async with await psycopg.AsyncConnection.connect(DB_DSN) as conn:
        async with conn.cursor() as cur:
            await cur.execute(CREATE_TABLE_SQL)
        await conn.commit()

    # Дальше — через пул, чтобы 12 параллельных корутин не дрались за одно соединение
    async with AsyncConnectionPool(DB_DSN, min_size=1, max_size=5, open=False) as pool:
        await pool.wait()
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *(parse_and_save(session, pool, url) for url in URLS)
            )


def run() -> float:
    t0 = time.perf_counter()
    asyncio.run(_run_async())
    elapsed = time.perf_counter() - t0
    print(f"[async] Готово. Время: {elapsed:.2f} сек")
    return elapsed


def main() -> None:
    print(f"[async] Парсим {len(URLS)} страниц Wikipedia асинхронно")
    run()


if __name__ == "__main__":
    main()
