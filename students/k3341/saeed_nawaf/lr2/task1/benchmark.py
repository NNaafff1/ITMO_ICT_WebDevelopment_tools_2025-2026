"""
Утилита для сравнения всех трёх подходов на одинаковом меньшем N.

Полные программы (sum_threading.py, sum_multiprocessing.py, sum_async.py)
считают сумму до 10^13 согласно заданию. На обычном ноутбуке это может
занимать часы (особенно для threading из-за GIL).

Этот файл запускает все три реализации на меньшем N для быстрой
демонстрации разницы во времени работы. Для отчёта рекомендуется
запускать именно его, а также один-два прогона основных файлов на
полном N, чтобы зафиксировать результат.
"""
import asyncio
import multiprocessing as mp
import threading
import time

# Меньшее значение для быстрого сравнения — порядка 10^8.
# При желании увеличьте до 10^9 или 10^10.
N = 100_000_000
NUM_WORKERS = 4


# --------- threading ---------
def _thread_worker(start, end, out, idx):
    s = 0
    for i in range(start, end + 1):
        s += i
    out[idx] = s


def run_threading():
    out = [0] * NUM_WORKERS
    threads = []
    chunk = N // NUM_WORKERS
    t0 = time.perf_counter()
    for i in range(NUM_WORKERS):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < NUM_WORKERS - 1 else N
        t = threading.Thread(target=_thread_worker, args=(s, e, out, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t0
    return sum(out), elapsed


# --------- multiprocessing ---------
def _mp_worker(args):
    start, end = args
    s = 0
    for i in range(start, end + 1):
        s += i
    return s


def run_multiprocessing():
    chunk = N // NUM_WORKERS
    ranges = [
        (i * chunk + 1, (i + 1) * chunk if i < NUM_WORKERS - 1 else N)
        for i in range(NUM_WORKERS)
    ]
    t0 = time.perf_counter()
    with mp.Pool(NUM_WORKERS) as pool:
        partial = pool.map(_mp_worker, ranges)
    elapsed = time.perf_counter() - t0
    return sum(partial), elapsed


# --------- async ---------
def _sum_range(start, end):
    s = 0
    for i in range(start, end + 1):
        s += i
    return s


async def _async_task(start, end):
    return await asyncio.to_thread(_sum_range, start, end)


async def _run_async():
    chunk = N // NUM_WORKERS
    tasks = []
    for i in range(NUM_WORKERS):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < NUM_WORKERS - 1 else N
        tasks.append(_async_task(s, e))
    t0 = time.perf_counter()
    partial = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - t0
    return sum(partial), elapsed


def run_async():
    return asyncio.run(_run_async())


def main():
    expected = N * (N + 1) // 2
    print(f"=== Сравнение подходов на N = {N:,} ===\n")

    print("threading...")
    s, t = run_threading()
    print(f"  результат: {s} (корректно: {s == expected}), время: {t:.2f} сек\n")

    print("multiprocessing...")
    s, t = run_multiprocessing()
    print(f"  результат: {s} (корректно: {s == expected}), время: {t:.2f} сек\n")

    print("async (to_thread)...")
    s, t = run_async()
    print(f"  результат: {s} (корректно: {s == expected}), время: {t:.2f} сек\n")

    print("Ожидаемый результат:", expected)


if __name__ == "__main__":
    main()
