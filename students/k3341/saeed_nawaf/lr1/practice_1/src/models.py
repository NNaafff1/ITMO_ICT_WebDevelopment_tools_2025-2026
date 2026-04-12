from typing import Optional, List
from pydantic import BaseModel


class Profession(BaseModel):
    id: int
    title: str
    description: str


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Warrior(BaseModel):
    id: int
    race: str
    name: str
    level: int
    profession: Optional[Profession] = None
    skills: List[Skill] = []


class WarriorCreate(BaseModel):
    race: str
    name: str
    level: int
    profession_id: Optional[int] = None
    skill_ids: List[int] = []


class WarriorUpdate(BaseModel):
    race: Optional[str] = None
    name: Optional[str] = None
    level: Optional[int] = None
    profession_id: Optional[int] = None
    skill_ids: Optional[List[int]] = None


class ProfessionCreate(BaseModel):
    title: str
    description: str


class SkillCreate(BaseModel):
    name: str
    description: str
