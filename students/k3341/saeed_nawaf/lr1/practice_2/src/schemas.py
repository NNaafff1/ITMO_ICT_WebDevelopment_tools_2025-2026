from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ProfessionCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProfessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None


class SkillCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class WarriorCreate(BaseModel):
    race: str
    name: str
    level: int = 1
    profession_id: Optional[int] = None
    skill_ids: List[int] = []


class WarriorUpdate(BaseModel):
    race: Optional[str] = None
    name: Optional[str] = None
    level: Optional[int] = None
    profession_id: Optional[int] = None
    skill_ids: Optional[List[int]] = None


class WarriorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    race: str
    name: str
    level: int
    profession: Optional[ProfessionResponse] = None
    skills: List[SkillResponse] = []
