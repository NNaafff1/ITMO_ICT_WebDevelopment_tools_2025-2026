from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.database import Base

warrior_skills = Table(
    "warrior_skills",
    Base.metadata,
    Column("warrior_id", Integer, ForeignKey("warriors.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


class Profession(Base):
    __tablename__ = "professions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(String(300))

    warriors = relationship("Warrior", back_populates="profession")


class Warrior(Base):
    __tablename__ = "warriors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    race = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    profession_id = Column(Integer, ForeignKey("professions.id"), nullable=True)

    profession = relationship("Profession", back_populates="warriors")
    skills = relationship("Skill", secondary=warrior_skills, back_populates="warriors")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(300))

    warriors = relationship("Warrior", secondary=warrior_skills, back_populates="skills")
