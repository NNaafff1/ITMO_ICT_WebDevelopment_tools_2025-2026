"""
Задача 1 — подсчёт суммы чисел от 1 до N с использованием asyncio.

ВАЖНО: asyncio предназначен для I/O-bound задач (сеть, диск), а не для
CPU-bound. Сам по себе asyncio выполняет код в одном потоке, поэтому
для тяжёлых вычислений он будет даже МЕДЛЕННЕЕ, чем однопоточный код,
если просто завернуть calculate_sum в async-функцию.

Чтобы получить реальный выигрыш, мы используем asyncio.to_thread,
который под капотом запускает вычисления в ThreadPoolExecutor. Это всё
равно ограничено GIL, но позволяет показать корректное использование
async/await для распараллеливания.

Учебная цель этого варианта — показать, что asyncio сам по себе не
ускоряет CPU-bound работу, и продемонстрировать правильную интеграцию
синхронного кода в async-окружение.
"""
import asyncio
import time

N = 10_000_000_000_000  # 10^13
NUM_TASKS = 4


def _sum_range(start: int, end: int) -> int:
    """Синхронная функция, считающая сумму на диапазоне."""
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def calculate_sum(start: int, end: int) -> int:
    """Асинхронная обёртка — выполняет вычисления в отдельном потоке."""
    return await asyncio.to_thread(_sum_range, start, end)


async def main() -> None:
    print(f"[async] Считаем сумму от 1 до {N:,} в {NUM_TASKS} задачах")
    print("[async] ВНИМАНИЕ: asyncio для CPU-bound даёт прирост только через to_thread,")
    print("[async] и всё равно ограничен GIL. Это и есть учебная демонстрация.")

    chunk_size = N // NUM_TASKS
    tasks = []
    for i in range(NUM_TASKS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_TASKS - 1 else N
        tasks.append(calculate_sum(start, end))

    start_time = time.perf_counter()
    partial_sums = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start_time

    total = sum(partial_sums)
    expected = N * (N + 1) // 2
    print(f"[async] Сумма  = {total}")
    print(f"[async] Ожид.  = {expected}")
    print(f"[async] Совпало: {total == expected}")
    print(f"[async] Время:  {elapsed:.2f} сек")


if __name__ == "__main__":
    asyncio.run(main())
