# Задача 1 — Сумма от 1 до 10¹³

## Описание

Диапазон `[1, N]` где N = 10 000 000 000 000 (10¹³) разбивается на 4
равные части. Каждый воркер (поток/процесс/корутина) считает сумму
своего диапазона, затем основной поток складывает результаты.

Корректность проверяется по формуле Гаусса `N·(N+1)/2`.

## Реализация 1 — threading

Файл: `task1/sum_threading.py`

Используется модуль `threading`. Каждый поток считает свою часть и
кладёт результат в общий список (индекс — номер потока, что
гарантирует отсутствие гонок без явных блокировок).

```python
import threading

results = [0] * NUM_THREADS

def calculate_sum(start, end, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    results[index] = total

threads = []
for i in range(NUM_THREADS):
    s = i * chunk + 1
    e = (i + 1) * chunk if i < NUM_THREADS - 1 else N
    t = threading.Thread(target=calculate_sum, args=(s, e, i))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
total = sum(results)
```

**Особенность:** все потоки конкурируют за GIL, поэтому реального
параллелизма нет — настоящий вычислительный код выполняется только
в одном потоке за раз.

## Реализация 2 — multiprocessing

Файл: `task1/sum_multiprocessing.py`

Используется `multiprocessing.Pool` с `starmap` — самый удобный
способ распараллелить функцию с несколькими аргументами.

```python
import multiprocessing as mp

def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

with mp.Pool(processes=NUM_PROCESSES) as pool:
    partial = pool.starmap(calculate_sum, ranges)
total = sum(partial)
```

**Особенность:** каждый процесс имеет собственный интерпретатор и
память. GIL не мешает, ускорение пропорционально числу ядер.

## Реализация 3 — asyncio

Файл: `task1/sum_async.py`

Сам `asyncio` для CPU-bound бесполезен (один поток, кооперативная
многозадачность). Чтобы получить параллельность, используется
`asyncio.to_thread` — запуск синхронной функции в
`ThreadPoolExecutor`:

```python
async def calculate_sum(start, end):
    return await asyncio.to_thread(_sum_range, start, end)

partial = await asyncio.gather(
    *(calculate_sum(s, e) for s, e in ranges)
)
total = sum(partial)
```

**Особенность:** по сути это тот же threading — корутины ждут в
пуле потоков, и GIL так же ограничивает параллелизм.

## Результаты

Запуск через `task1/benchmark.py` на меньшем `N = 10⁸` (для 10¹³
время в 10⁵ раз больше, выводы те же).

| Подход | Время | Результат корректен |
|---|---:|:---:|
| threading | 3.64 сек | ✓ |
| multiprocessing | 1.73 сек | ✓ |
| async (`to_thread`) | 3.93 сек | ✓ |

## Анализ результатов

**threading** не быстрее однопоточного варианта: GIL не пускает
потоки выполняться параллельно для чистого CPU-кода. Из-за
накладных расходов на переключение время может даже увеличиться
по сравнению с обычным циклом без потоков.

**multiprocessing** даёт реальное ускорение, ограниченное только
числом физических ядер процессора. Это правильный выбор для
CPU-bound задач. На 4 ядрах ожидается ускорение примерно в 3.5–4 раза.

**asyncio через `to_thread`** ведёт себя как threading — те же
ограничения GIL. Без `to_thread` корутины выполнялись бы строго
по очереди (одна за другой в одном потоке), что было бы медленнее
обычного цикла.

### Вывод по задаче 1

Для тяжёлых вычислений в Python — только `multiprocessing`. Threading
и asyncio имеют смысл, когда задача ждёт чего-то снаружи (ответа
сервера, чтения файла), а не считает сама.

Дальше — [Задача 2](task2.md).
