"""
Сравнение трёх подходов парсинга. Запускает scrape_threading,
scrape_multiprocessing и scrape_async по очереди, печатает итоговую
таблицу времени.

Запускайте после того, как каждый из трёх scrape_*.py уже отработал
успешно хотя бы один раз (т.е. БД и таблица skills готовы).
"""
import scrape_async
import scrape_multiprocessing
import scrape_threading


def main() -> None:
    print("\n=== threading ===")
    t_threading = scrape_threading.run()

    print("\n=== multiprocessing ===")
    t_mp = scrape_multiprocessing.run()

    print("\n=== async ===")
    t_async = scrape_async.run()

    print("\n=== Итоги ===")
    print(f"threading:        {t_threading:6.2f} сек")
    print(f"multiprocessing:  {t_mp:6.2f} сек")
    print(f"async:            {t_async:6.2f} сек")


if __name__ == "__main__":
    main()
