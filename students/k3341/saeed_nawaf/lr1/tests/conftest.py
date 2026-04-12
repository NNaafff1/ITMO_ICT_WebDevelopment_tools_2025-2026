import os
import sys

# Override DATABASE_URL before any app imports
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Add laboratory_work to sys.path so "from src." imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "laboratory_work"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "skills": "Python,FastAPI"
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_project(client, auth_headers):
    response = client.post("/projects/", json={
        "title": "Test Project",
        "description": "A test project for finding teammates",
        "required_skills": "Python,Docker",
        "status": "open"
    }, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_user_headers(client):
    client.post("/auth/register", json={
        "username": "seconduser",
        "email": "second@example.com",
        "password": "secondpass123",
        "full_name": "Second User",
        "skills": "JavaScript,React"
    })
    response = client.post("/auth/login", data={
        "username": "seconduser",
        "password": "secondpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
