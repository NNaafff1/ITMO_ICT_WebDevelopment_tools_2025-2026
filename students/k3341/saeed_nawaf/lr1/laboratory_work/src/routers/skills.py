from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import SkillCreate, SkillResponse, UserSkillCreate, UserSkillResponse
from src import crud
from src.auth import get_current_user

router = APIRouter(tags=["Skills"])


@router.post("/skills/", response_model=SkillResponse, status_code=201)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new skill (auth required)."""
    return crud.create_skill(db, skill)


@router.get("/skills/", response_model=list[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    """List all available skills."""
    return crud.get_skills(db)


@router.post("/users/{user_id}/skills", response_model=UserSkillResponse, status_code=201)
def add_skill_to_user(user_id: int, user_skill: UserSkillCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Add a skill to a user's profile (auth required, own profile only)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    skill = crud.get_skill(db, user_skill.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return crud.add_user_skill(db, user_id, user_skill.skill_id, user_skill.level)


@router.get("/users/{user_id}/skills", response_model=list[UserSkillResponse])
def get_user_skills(user_id: int, db: Session = Depends(get_db)):
    """Get all skills of a user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_user_skills(db, user_id)
