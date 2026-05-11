# Запуск проекта

## Подготовка базы данных

Используется БД `teamfinder` из лабораторной работы №1. Если контейнер
из Lab 1 уже запущен — пропустите этот шаг.

```bash
cd lab1/laboratory_work
docker compose up -d db
```

Параметры подключения берутся из `lab2/task2/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=teamfinder
```

## Установка зависимостей

```bash
cd lab2
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Задача 1 — сумма от 1 до 10¹³

Полные программы согласно заданию:

```bash
python task1/sum_threading.py          # очень долго: GIL душит CPU-bound
python task1/sum_multiprocessing.py    # реальное распараллеливание
python task1/sum_async.py              # asyncio + to_thread
```

Быстрый прогон всех трёх на меньшем N (для замеров в таблицу):

```bash
python task1/benchmark.py
```

## Задача 2 — парсинг + БД

Каждый из трёх парсеров заполняет таблицу `skills` БД `teamfinder`:

```bash
python task2/scrape_threading.py
python task2/scrape_multiprocessing.py
python task2/scrape_async.py
```

Сравнение всех трёх в одной таблице:

```bash
python task2/benchmark.py
```

## Проверка результата в БД

```bash
docker exec -it <container_name> psql -U postgres -d teamfinder \
  -c "SELECT id, name FROM skills ORDER BY id;"
```

`<container_name>` берётся из `docker ps`.

## Локальный просмотр документации

```bash
pip install mkdocs mkdocs-material
mkdocs serve     # http://127.0.0.1:8000
```

## Деплой документации на GitHub Pages

Документация публикуется автоматически при пуше в ветку `lab2` через
GitHub Actions (`.github/workflows/lab2-docs.yml`).

Ручной деплой:

```bash
cd lab2
mkdocs gh-deploy --force
```
