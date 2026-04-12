from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers import auth, users, projects, team_requests, skills
import src.models  # noqa: F401 — register all models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Team Finder API",
    description="A platform for finding teammates for your projects — ITMO Lab 1",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(team_requests.router)
app.include_router(skills.router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check — confirms the API is running."""
    return {"status": "ok", "message": "Team Finder API is running"}
