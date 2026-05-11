"""
Общая функция парсинга Wikipedia-страницы языка программирования.

Возвращает кортеж (name, description), где:
- name        — название из <h1 id="firstHeading">, очищенное от скобок
                "(programming language)" и обрезанное до 100 символов
                (ограничение колонки в БД).
- description — первый содержательный абзац статьи, обрезанный до 300 символов.
"""
import re

from bs4 import BeautifulSoup


def parse_wiki_page(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # Заголовок
    h1 = soup.select_one("h1#firstHeading")
    raw_title = h1.get_text(strip=True) if h1 else "(unknown)"
    # Убираем "(programming language)" и подобное
    name = re.sub(r"\s*\([^)]*\)\s*", "", raw_title).strip()
    name = name[:100]  # колонка VARCHAR(100)

    # Первый содержательный абзац основного контента
    content = soup.select_one("div.mw-parser-output") or soup
    description = ""
    for p in content.find_all("p", recursive=True):
        text = p.get_text(" ", strip=True)
        if len(text) > 50:  # пропускаем пустышки и навигационные абзацы
            description = text
            break
    # Чистим [1][2] ссылки на сноски
    description = re.sub(r"\[\d+\]", "", description)
    description = description[:300]  # колонка VARCHAR(300)

    return name, description
