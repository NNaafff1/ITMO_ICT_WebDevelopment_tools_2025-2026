from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import Base, engine, get_db
from src.schemas import (
    WarriorCreate, WarriorUpdate, WarriorResponse,
    ProfessionCreate, ProfessionResponse,
    SkillCreate, SkillResponse,
)
from src import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Practice 2 — Database Integration",
    description="SQLAlchemy + SQLite with many-to-many relationships and nested display",
    version="1.0.0",
)


# ── Warriors ─────────────────────────────────────────────────────────

@app.post("/warriors/", response_model=WarriorResponse, status_code=201, tags=["Warriors"])
def create_warrior(data: WarriorCreate, db: Session = Depends(get_db)):
    """Create a warrior with optional profession and skills."""
    return crud.create_warrior(db, data)


@app.get("/warriors/", response_model=list[WarriorResponse], tags=["Warriors"])
def list_warriors(db: Session = Depends(get_db)):
    """List all warriors with nested profession and skills."""
    return crud.get_warriors(db)


@app.get("/warriors/{warrior_id}", response_model=WarriorResponse, tags=["Warriors"])
def get_warrior(warrior_id: int, db: Session = Depends(get_db)):
    """Get one warrior with full nested objects."""
    warrior = crud.get_warrior(db, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.put("/warriors/{warrior_id}", response_model=WarriorResponse, tags=["Warriors"])
def update_warrior(warrior_id: int, data: WarriorUpdate, db: Session = Depends(get_db)):
    """Update a warrior."""
    warrior = crud.update_warrior(db, warrior_id, data)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.delete("/warriors/{warrior_id}", status_code=204, tags=["Warriors"])
def delete_warrior(warrior_id: int, db: Session = Depends(get_db)):
    """Delete a warrior."""
    if not crud.delete_warrior(db, warrior_id):
        raise HTTPException(status_code=404, detail="Warrior not found")


@app.post("/warriors/{warrior_id}/skills/{skill_id}", response_model=WarriorResponse, tags=["Warriors"])
def add_skill_to_warrior(warrior_id: int, skill_id: int, db: Session = Depends(get_db)):
    """Add a skill to a warrior."""
    warrior = crud.add_skill_to_warrior(db, warrior_id, skill_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior or skill not found")
    return warrior


@app.delete("/warriors/{warrior_id}/skills/{skill_id}", status_code=204, tags=["Warriors"])
def remove_skill_from_warrior(warrior_id: int, skill_id: int, db: Session = Depends(get_db)):
    """Remove a skill from a warrior."""
    warrior = crud.remove_skill_from_warrior(db, warrior_id, skill_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior or skill not found")


# ── Professions ──────────────────────────────────────────────────────

@app.post("/professions/", response_model=ProfessionResponse, status_code=201, tags=["Professions"])
def create_profession(data: ProfessionCreate, db: Session = Depends(get_db)):
    """Create a profession."""
    return crud.create_profession(db, data)


@app.get("/professions/", response_model=list[ProfessionResponse], tags=["Professions"])
def list_professions(db: Session = Depends(get_db)):
    """List all professions."""
    return crud.get_professions(db)


@app.get("/professions/{profession_id}", response_model=ProfessionResponse, tags=["Professions"])
def get_profession(profession_id: int, db: Session = Depends(get_db)):
    """Get one profession."""
    prof = crud.get_profession(db, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    return prof


@app.delete("/professions/{profession_id}", status_code=204, tags=["Professions"])
def delete_profession(profession_id: int, db: Session = Depends(get_db)):
    """Delete a profession."""
    if not crud.delete_profession(db, profession_id):
        raise HTTPException(status_code=404, detail="Profession not found")


# ── Skills ───────────────────────────────────────────────────────────

@app.post("/skills/", response_model=SkillResponse, status_code=201, tags=["Skills"])
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    """Create a skill."""
    return crud.create_skill(db, data)


@app.get("/skills/", response_model=list[SkillResponse], tags=["Skills"])
def list_skills(db: Session = Depends(get_db)):
    """List all skills."""
    return crud.get_skills(db)


@app.get("/skills/{skill_id}", response_model=SkillResponse, tags=["Skills"])
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get one skill."""
    skill = crud.get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.delete("/skills/{skill_id}", status_code=204, tags=["Skills"])
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    """Delete a skill."""
    if not crud.delete_skill(db, skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8002, reload=True)
