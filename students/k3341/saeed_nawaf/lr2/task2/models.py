"""
Модель таблицы `skills` БД teamfinder из Lab 1.

Парсеры заполняют эту таблицу данными с Wikipedia (имя языка +
краткое описание). Здесь модель приведена для документирования схемы;
сами парсеры работают через psycopg (асинхронный режим) напрямую
с raw SQL, потому что это проще и быстрее, чем SQLAlchemy ORM.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=True)

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name!r}>"
