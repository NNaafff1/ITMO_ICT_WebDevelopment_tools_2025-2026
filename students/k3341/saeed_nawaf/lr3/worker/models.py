"""
Минимальная модель Skill для воркера. Совпадает по схеме с моделью
api/src/models.py из Lab 1 — таблица та же, поля те же.

Дублирование сделано осознанно: воркер живёт в своём контейнере и не
должен зависеть от кода API-сервиса. В реальном проекте схема обычно
выносится в shared-пакет, но для учебной лабы дубль чище и понятнее.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=True)
