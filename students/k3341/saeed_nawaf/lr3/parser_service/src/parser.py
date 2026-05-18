"""
Логика парсинга Wikipedia-страниц. Прямой перенос из Lab 2
(task2/parser_common.py) с добавлением функции fetch_and_parse,
которая объединяет HTTP-запрос и парсинг в одну операцию.

Используется как сервисом-парсером (через HTTP POST /parse),
так и Celery-воркером (напрямую импортируется в задаче).
"""
import re

import requests
from bs4 import BeautifulSoup

HTTP_HEADERS = {
    "User-Agent": "Lab3-Parser/1.0 (educational project)",
}
HTTP_TIMEOUT = 15


def parse_wiki_page(html: str) -> tuple[str, str]:
    """Извлекает (name, description) из HTML Wikipedia-страницы.

    Логика:
    - name берётся из <h1 id="firstHeading">, очищается от "(programming
      language)" и обрезается до 100 символов (ограничение колонки skills.name).
    - description — первый абзац длиной более 50 символов из основного
      контента, сноски [N] удаляются, обрезается до 300 символов.
    """
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.select_one("h1#firstHeading")
    raw_title = h1.get_text(strip=True) if h1 else "(unknown)"
    name = re.sub(r"\s*\([^)]*\)\s*", "", raw_title).strip()[:100]

    content = soup.select_one("div.mw-parser-output") or soup
    description = ""
    for p in content.find_all("p", recursive=True):
        text = p.get_text(" ", strip=True)
        if len(text) > 50:
            description = text
            break
    description = re.sub(r"\[\d+\]", "", description)[:300]

    return name, description


def fetch_and_parse(url: str) -> tuple[str, str]:
    """Скачивает страницу и парсит. Бросает исключение при сетевой ошибке."""
    resp = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return parse_wiki_page(resp.text)
