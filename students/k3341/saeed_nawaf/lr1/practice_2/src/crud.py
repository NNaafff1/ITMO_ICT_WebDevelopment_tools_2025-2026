from typing import Optional, List
from sqlalchemy.orm import Session
from src.models import Warrior, Profession, Skill
from src.schemas import WarriorCreate, WarriorUpdate, ProfessionCreate, SkillCreate


# ── Professions ──────────────────────────────────────────────────────

def create_profession(db: Session, data: ProfessionCreate) -> Profession:
    prof = Profession(title=data.title, description=data.description)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


def get_professions(db: Session) -> list[Profession]:
    return db.query(Profession).all()


def get_profession(db: Session, profession_id: int) -> Optional[Profession]:
    return db.query(Profession).filter(Profession.id == profession_id).first()


def delete_profession(db: Session, profession_id: int) -> bool:
    prof = get_profession(db, profession_id)
    if not prof:
        return False
    db.delete(prof)
    db.commit()
    return True


# ── Skills ───────────────────────────────────────────────────────────

def create_skill(db: Session, data: SkillCreate) -> Skill:
    skill = Skill(name=data.name, description=data.description)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def get_skills(db: Session) -> list[Skill]:
    return db.query(Skill).all()


def get_skill(db: Session, skill_id: int) -> Optional[Skill]:
    return db.query(Skill).filter(Skill.id == skill_id).first()


def delete_skill(db: Session, skill_id: int) -> bool:
    skill = get_skill(db, skill_id)
    if not skill:
        return False
    db.delete(skill)
    db.commit()
    return True


# ── Warriors ─────────────────────────────────────────────────────────

def create_warrior(db: Session, data: WarriorCreate) -> Warrior:
    warrior = Warrior(race=data.race, name=data.name, level=data.level,
                      profession_id=data.profession_id)
    if data.skill_ids:
        skill_objs = db.query(Skill).filter(Skill.id.in_(data.skill_ids)).all()
        warrior.skills = skill_objs
    db.add(warrior)
    db.commit()
    db.refresh(warrior)
    return warrior


def get_warriors(db: Session) -> list[Warrior]:
    return db.query(Warrior).all()


def get_warrior(db: Session, warrior_id: int) -> Optional[Warrior]:
    return db.query(Warrior).filter(Warrior.id == warrior_id).first()


def update_warrior(db: Session, warrior_id: int, data: WarriorUpdate) -> Optional[Warrior]:
    warrior = get_warrior(db, warrior_id)
    if not warrior:
        return None
    update = data.model_dump(exclude_unset=True)
    skill_ids = update.pop("skill_ids", None)
    for key, value in update.items():
        setattr(warrior, key, value)
    if skill_ids is not None:
        skill_objs = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
        warrior.skills = skill_objs
    db.commit()
    db.refresh(warrior)
    return warrior


def delete_warrior(db: Session, warrior_id: int) -> bool:
    warrior = get_warrior(db, warrior_id)
    if not warrior:
        return False
    db.delete(warrior)
    db.commit()
    return True


def add_skill_to_warrior(db: Session, warrior_id: int, skill_id: int) -> Optional[Warrior]:
    warrior = get_warrior(db, warrior_id)
    skill = get_skill(db, skill_id)
    if not warrior or not skill:
        return None
    if skill not in warrior.skills:
        warrior.skills.append(skill)
        db.commit()
        db.refresh(warrior)
    return warrior


def remove_skill_from_warrior(db: Session, warrior_id: int, skill_id: int) -> Optional[Warrior]:
    warrior = get_warrior(db, warrior_id)
    skill = get_skill(db, skill_id)
    if not warrior or not skill:
        return None
    if skill in warrior.skills:
        warrior.skills.remove(skill)
        db.commit()
        db.refresh(warrior)
    return warrior
