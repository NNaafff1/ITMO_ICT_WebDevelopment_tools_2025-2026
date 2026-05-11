"""
Задача 1 — подсчёт суммы чисел от 1 до N с использованием multiprocessing.

В отличие от threading, multiprocessing создаёт отдельные процессы, каждый
со своим интерпретатором Python и своей памятью. GIL на это не действует,
поэтому для CPU-bound задач это даёт реальное ускорение пропорционально
числу ядер процессора.
"""
import multiprocessing as mp
import time

N = 10_000_000_000_000  # 10^13
NUM_PROCESSES = 4


def calculate_sum(start: int, end: int) -> int:
    """Считает сумму целых чисел в диапазоне [start, end] включительно."""
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def main() -> None:
    print(f"[multiprocessing] Считаем сумму от 1 до {N:,} в {NUM_PROCESSES} процессах")

    chunk_size = N // NUM_PROCESSES
    ranges = []
    for i in range(NUM_PROCESSES):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_PROCESSES - 1 else N
        ranges.append((start, end))

    start_time = time.perf_counter()

    with mp.Pool(processes=NUM_PROCESSES) as pool:
        partial_sums = pool.starmap(calculate_sum, ranges)

    total = sum(partial_sums)
    elapsed = time.perf_counter() - start_time

    expected = N * (N + 1) // 2
    print(f"[multiprocessing] Сумма  = {total}")
    print(f"[multiprocessing] Ожид.  = {expected}")
    print(f"[multiprocessing] Совпало: {total == expected}")
    print(f"[multiprocessing] Время:  {elapsed:.2f} сек")


if __name__ == "__main__":
    # на Windows / macOS обязательно нужна защита __main__ для multiprocessing
    main()
