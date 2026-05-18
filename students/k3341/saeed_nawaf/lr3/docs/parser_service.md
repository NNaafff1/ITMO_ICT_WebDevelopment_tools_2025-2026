# Сервис-парсер

## Подзадача 2 из ТЗ

Добавить в FastAPI эндпоинт, который принимает URL от клиента,
обращается к парсеру в отдельном контейнере и возвращает результат.

## Сервис-парсер: FastAPI в отдельном контейнере

`parser_service/src/main.py` — минимальное FastAPI-приложение с одним
содержательным эндпоинтом:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from src.parser import fetch_and_parse

app = FastAPI(title="TeamFinder Parser Service")


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    url: str
    name: str
    description: str


@app.post("/parse", response_model=ParseResponse)
def parse(request: ParseRequest) -> ParseResponse:
    try:
        name, description = fetch_and_parse(str(request.url))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parse failed: {exc}")
    return ParseResponse(url=str(request.url), name=name, description=description)
```

**Что важно:**

- **HttpUrl в Pydantic** — невалидные URL отсекаются на уровне
  валидации (422 Unprocessable Entity), эндпоинт даже не вызывается.
- **Сервис ничего не знает про БД.** Он принимает URL, возвращает
  распарсенные данные. За сохранение отвечает вызывающая сторона. Это
  даёт чистое разделение: парсер можно тестировать изолированно, и
  он не зависит от схемы БД.
- **Никаких зависимостей кроме `requests`, `beautifulsoup4`,
  `fastapi`.** Самый лёгкий образ из трёх.

## Логика парсинга (parser.py)

Прямой перенос из Lab 2 `task2/parser_common.py`. Извлекает заголовок
из `h1#firstHeading`, очищает от «(programming language)», берёт
первый содержательный абзац и обрезает до длин колонок БД (100 и 300).

```python
def parse_wiki_page(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.select_one("h1#firstHeading")
    raw_title = h1.get_text(strip=True) if h1 else "(unknown)"
    name = re.sub(r"\s*\([^)]*\)\s*", "", raw_title).strip()[:100]

    content = soup.select_one("div.mw-parser-output") or soup
    description = ""
    for p in content.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 50:
            description = text
            break
    description = re.sub(r"\[\d+\]", "", description)[:300]
    return name, description
```

## Синхронный эндпоинт в основном API

`api/src/routers/parser.py` — роутер с тремя эндпоинтами. Синхронный
вариант:

```python
@router.post("/parse", response_model=SkillResponse, status_code=201)
def parse_sync(
    request: ParseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        resp = requests.post(
            f"{PARSER_URL}/parse",
            json={"url": str(request.url)},
            timeout=PARSER_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Parser service unavailable: {exc}")

    name = data["name"]
    description = data["description"]

    existing = db.query(Skill).filter(Skill.name == name).first()
    if existing:
        existing.description = description
        db.commit()
        db.refresh(existing)
        return existing

    return crud.create_skill(db, SkillCreate(name=name, description=description))
```

**Что важно:**

- **`PARSER_URL` берётся из окружения.** Внутри compose это
  `http://parser:8001`. Локально (без docker) можно переопределить
  на `http://localhost:8001`.
- **Защита авторизацией.** Анонимы не должны нагружать парсер —
  любой вызов требует JWT-токен (тот же механизм, что и в Lab 1).
- **502 Bad Gateway, если парсер недоступен.** Это правильный код:
  наше API в порядке, но апстрим-сервис не отвечает. 500 был бы
  обманом, он подразумевает баг в нашем коде.
- **UPSERT по name.** Повторный парсинг той же страницы не падает на
  `UNIQUE`-ограничении, а обновляет описание. Это аккуратнее, чем
  пытаться отдать `ON CONFLICT` через ORM.

## Поведение при разных входных данных

| Запрос | Код | Что вернёт |
|---|---|---|
| Нет JWT | 401 | `Not authenticated` |
| `url`: `"not-a-url"` | 422 | Pydantic-валидация URL |
| Валидный URL, парсер не отвечает | 502 | `Parser service unavailable: ...` |
| Валидный URL, парсер вернул 500 | 502 | (внешний сервис плохо себя ведёт) |
| Валидный URL, всё ОК | 201 | `SkillResponse` с `id`, `name`, `description` |
