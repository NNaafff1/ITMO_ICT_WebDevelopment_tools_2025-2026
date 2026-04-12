# Practice 3 — JWT Authentication with Alembic

Demonstrates JWT authentication with FastAPI, SQLAlchemy, and Alembic migrations.

## .env integration with Alembic

The `migrations/env.py` file uses `python-dotenv` to load the `DATABASE_URL` from the `.env` file.
This allows Alembic to read the database connection string from environment configuration
rather than having it hardcoded in `alembic.ini`.

```python
from dotenv import load_dotenv
import os
load_dotenv()
database_url = os.getenv("DATABASE_URL", "sqlite:///./practice_3.db")
config.set_main_option("sqlalchemy.url", database_url)
```

The `.env` file contains:
```
DATABASE_URL=sqlite:///./practice_3.db
SECRET_KEY=practice3secretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Run
```bash
cd practice_3
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload --port 8003
```
