# Скриншоты

Иллюстрации работы программ.

## Задача 1 — Сумма от 1 до 10¹³

### Запуск `task1/benchmark.py`

Сравнение трёх подходов на одинаковом N. Multiprocessing — в ~2 раза
быстрее, threading и async проигрывают из-за GIL.

![Task 1 benchmark](screenshots/task1_benchmark.png)

## Задача 2 — Параллельный парсинг

### Запуск `task2/scrape_threading.py`

Парсинг 12 страниц Wikipedia в потоках. Все 12 навыков сохранены в БД.

![Task 2 threading](screenshots/task2_threading.png)

### Сравнение всех трёх подходов (`task2/benchmark.py`)

Async выиграл почти в 8 раз — идеальный результат для I/O-bound нагрузки.

![Task 2 benchmark](screenshots/task2_benchmark.png)

### Содержимое таблицы `skills` в БД

12 записей с навыками — заголовки и описания со страниц Wikipedia.

![DB skills table](screenshots/db_skills.png)
