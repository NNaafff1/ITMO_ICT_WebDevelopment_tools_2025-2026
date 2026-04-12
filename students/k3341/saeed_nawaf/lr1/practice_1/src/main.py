from fastapi import FastAPI, HTTPException
from src.models import (
    Warrior, WarriorCreate, WarriorUpdate,
    Profession, ProfessionCreate,
    Skill, SkillCreate,
)
from src.temp_db import warriors, professions, skills, counter, profession_counter, skill_counter

app = FastAPI(
    title="Practice 1 — FastAPI Basics",
    description="In-memory CRUD API with nested objects (one-to-one, one-to-many)",
    version="1.0.0",
)


def _build_warrior(raw: dict) -> dict:
    """Resolve a raw warrior dict into a full Warrior with nested objects."""
    prof = None
    if raw.get("profession_id") and raw["profession_id"] in professions:
        prof = professions[raw["profession_id"]]
    skill_list = [skills[sid] for sid in raw.get("skill_ids", []) if sid in skills]
    return {
        "id": raw["id"],
        "race": raw["race"],
        "name": raw["name"],
        "level": raw["level"],
        "profession": prof,
        "skills": skill_list,
    }


# ── Warriors ─────────────────────────────────────────────────────────

@app.get("/warriors/", response_model=list[Warrior], tags=["Warriors"])
def list_warriors():
    """List all warriors with nested profession and skills."""
    return [_build_warrior(w) for w in warriors.values()]


@app.get("/warriors/{warrior_id}", response_model=Warrior, tags=["Warriors"])
def get_warrior(warrior_id: int):
    """Get one warrior with nested profession and skills."""
    if warrior_id not in warriors:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return _build_warrior(warriors[warrior_id])


@app.post("/warriors/", response_model=Warrior, status_code=201, tags=["Warriors"])
def create_warrior(data: WarriorCreate):
    """Create a new warrior."""
    new_id = counter["value"]
    counter["value"] += 1
    raw = {"id": new_id, "race": data.race, "name": data.name, "level": data.level,
           "profession_id": data.profession_id, "skill_ids": data.skill_ids}
    warriors[new_id] = raw
    return _build_warrior(raw)


@app.put("/warriors/{warrior_id}", response_model=Warrior, tags=["Warriors"])
def update_warrior(warrior_id: int, data: WarriorUpdate):
    """Update a warrior."""
    if warrior_id not in warriors:
        raise HTTPException(status_code=404, detail="Warrior not found")
    raw = warriors[warrior_id]
    update = data.model_dump(exclude_unset=True)
    for key, value in update.items():
        raw[key] = value
    return _build_warrior(raw)


@app.delete("/warriors/{warrior_id}", status_code=204, tags=["Warriors"])
def delete_warrior(warrior_id: int):
    """Delete a warrior."""
    if warrior_id not in warriors:
        raise HTTPException(status_code=404, detail="Warrior not found")
    del warriors[warrior_id]


# ── Professions ──────────────────────────────────────────────────────

@app.get("/professions/", response_model=list[Profession], tags=["Professions"])
def list_professions():
    """List all professions."""
    return list(professions.values())


@app.get("/professions/{profession_id}", response_model=Profession, tags=["Professions"])
def get_profession(profession_id: int):
    """Get one profession."""
    if profession_id not in professions:
        raise HTTPException(status_code=404, detail="Profession not found")
    return professions[profession_id]


@app.post("/professions/", response_model=Profession, status_code=201, tags=["Professions"])
def create_profession(data: ProfessionCreate):
    """Create a profession."""
    new_id = profession_counter["value"]
    profession_counter["value"] += 1
    prof = {"id": new_id, "title": data.title, "description": data.description}
    professions[new_id] = prof
    return prof


@app.delete("/professions/{profession_id}", status_code=204, tags=["Professions"])
def delete_profession(profession_id: int):
    """Delete a profession."""
    if profession_id not in professions:
        raise HTTPException(status_code=404, detail="Profession not found")
    del professions[profession_id]


# ── Skills ───────────────────────────────────────────────────────────

@app.get("/skills/", response_model=list[Skill], tags=["Skills"])
def list_skills():
    """List all skills."""
    return list(skills.values())


@app.get("/skills/{skill_id}", response_model=Skill, tags=["Skills"])
def get_skill(skill_id: int):
    """Get one skill."""
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skills[skill_id]


@app.post("/skills/", response_model=Skill, status_code=201, tags=["Skills"])
def create_skill(data: SkillCreate):
    """Create a skill."""
    new_id = skill_counter["value"]
    skill_counter["value"] += 1
    sk = {"id": new_id, "name": data.name, "description": data.description}
    skills[new_id] = sk
    return sk


@app.delete("/skills/{skill_id}", status_code=204, tags=["Skills"])
def delete_skill(skill_id: int):
    """Delete a skill."""
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    del skills[skill_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)
