"""
Задача 1 — подсчёт суммы чисел от 1 до N с использованием threading.

ВНИМАНИЕ: Из-за GIL (Global Interpreter Lock) в CPython потоки НЕ дают
реального параллелизма для CPU-bound задач. Эта программа специально
демонстрирует, почему threading плохо подходит для подобных вычислений —
время выполнения будет примерно таким же (или хуже) чем у однопоточной
версии из-за накладных расходов на переключение потоков.

Это и есть учебная цель: увидеть разницу с multiprocessing.
"""
import threading
import time

N = 10_000_000_000_000  # 10^13 как в задании
NUM_THREADS = 4

# результаты потоков складываем сюда
results = [0] * NUM_THREADS


def calculate_sum(start: int, end: int, index: int) -> None:
    """Считает сумму целых чисел в диапазоне [start, end] включительно."""
    total = 0
    for i in range(start, end + 1):
        total += i
    results[index] = total


def main() -> None:
    print(f"[threading] Считаем сумму от 1 до {N:,} в {NUM_THREADS} потоках")
    print("[threading] ВНИМАНИЕ: из-за GIL это может занять очень много времени.")

    chunk_size = N // NUM_THREADS
    threads = []

    start_time = time.perf_counter()

    for i in range(NUM_THREADS):
        start = i * chunk_size + 1
        # последний поток забирает остаток, чтобы покрыть весь диапазон
        end = (i + 1) * chunk_size if i < NUM_THREADS - 1 else N
        t = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    elapsed = time.perf_counter() - start_time

    # проверка через формулу Гаусса n*(n+1)/2
    expected = N * (N + 1) // 2
    print(f"[threading] Сумма  = {total}")
    print(f"[threading] Ожид.  = {expected}")
    print(f"[threading] Совпало: {total == expected}")
    print(f"[threading] Время:  {elapsed:.2f} сек")


if __name__ == "__main__":
    main()
