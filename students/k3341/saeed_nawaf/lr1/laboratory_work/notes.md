# Laboratory Work 1 — Team Finder API

## How to run
```bash
cd laboratory_work
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload
```
API docs: http://localhost:8000/docs
