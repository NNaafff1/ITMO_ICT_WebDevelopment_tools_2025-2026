# Лабораторная работа 2

# Потоки. Процессы. Асинхронность

**Дата:** Май 2026

---

## Цель работы

Понять отличия между потоками (threading) и процессами (multiprocessing),
а также разобраться, что такое асинхронность (asyncio) в Python.
Научиться выбирать подходящий инструмент параллелизма в зависимости от
характера задачи: CPU-bound или I/O-bound.

## Задание

Реализовать две задачи:

1. **Задача 1.** Подсчитать сумму всех чисел от 1 до 10 000 000 000 000
   (10¹³) тремя способами — через `threading`, `multiprocessing` и
   `asyncio`. Разделить вычисления на параллельные подзадачи и сравнить
   время выполнения.

2. **Задача 2.** Реализовать параллельный парсинг нескольких веб-страниц
   с сохранением данных в БД из лабораторной работы №1. Тремя способами
   (`threading`, `multiprocessing`, `asyncio`). Подключение к БД сделать
   асинхронным.

## Содержание отчёта

1. [Теоретические основы](theory.md) — GIL, threading, multiprocessing, asyncio
2. [Задача 1 — Сумма от 1 до 10¹³](task1.md) — три реализации, замеры, анализ
3. [Задача 2 — Параллельный парсинг + БД](task2.md) — три парсера, асинхронный psycopg, анализ
4. [Итоговые выводы](conclusion.md)
5. [Запуск проекта](usage.md) — установка, команды, проверка

## Структура проекта

```
lab2/
├── mkdocs.yml
├── requirements.txt
├── docs/                            ← данный сайт
│   ├── index.md
│   ├── theory.md
│   ├── task1.md
│   ├── task2.md
│   ├── conclusion.md
│   └── usage.md
├── task1/
│   ├── sum_threading.py
│   ├── sum_multiprocessing.py
│   ├── sum_async.py
│   └── benchmark.py
└── task2/
    ├── .env
    ├── config.py
    ├── models.py
    ├── parser_common.py
    ├── scrape_threading.py
    ├── scrape_multiprocessing.py
    ├── scrape_async.py
    ├── benchmark.py
    └── requirements.txt
```
