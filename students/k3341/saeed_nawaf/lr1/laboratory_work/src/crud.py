from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models import User, Project, TeamRequest, ProjectMember, Skill, UserSkill
from src.schemas import UserCreate, UserUpdate, ProjectCreate, ProjectUpdate, TeamRequestCreate, SkillCreate
from src.auth import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, skill_filter: Optional[str] = None) -> list[User]:
    query = db.query(User)
    if skill_filter:
        query = query.filter(func.lower(User.skills).contains(func.lower(skill_filter)))
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        bio=user.bio,
        skills=user.skills,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> list[Project]:
    query = db.query(Project)
    if status_filter:
        query = query.filter(Project.status == status_filter)
    return query.offset(skip).limit(limit).all()


def get_projects_by_owner(db: Session, owner_id: int) -> list[Project]:
    return db.query(Project).filter(Project.owner_id == owner_id).all()


def create_project(db: Session, project: ProjectCreate, owner_id: int) -> Project:
    db_project = Project(
        title=project.title,
        description=project.description,
        required_skills=project.required_skills,
        owner_id=owner_id,
        status=project.status,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True


def get_team_request(db: Session, request_id: int) -> Optional[TeamRequest]:
    return db.query(TeamRequest).filter(TeamRequest.id == request_id).first()


def get_requests_by_sender(db: Session, sender_id: int) -> list[TeamRequest]:
    return db.query(TeamRequest).filter(TeamRequest.sender_id == sender_id).all()


def get_requests_by_project(db: Session, project_id: int) -> list[TeamRequest]:
    return db.query(TeamRequest).filter(TeamRequest.project_id == project_id).all()


def get_incoming_requests_for_user(db: Session, owner_id: int) -> list[TeamRequest]:
    return (
        db.query(TeamRequest)
        .join(Project, TeamRequest.project_id == Project.id)
        .filter(Project.owner_id == owner_id)
        .all()
    )


def create_team_request(db: Session, request: TeamRequestCreate, sender_id: int) -> TeamRequest:
    db_request = TeamRequest(
        project_id=request.project_id,
        sender_id=sender_id,
        message=request.message,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_request_status(db: Session, request_id: int, new_status: str) -> Optional[TeamRequest]:
    db_request = get_team_request(db, request_id)
    if not db_request:
        return None
    db_request.status = new_status
    db.commit()
    db.refresh(db_request)
    return db_request


def has_pending_request(db: Session, project_id: int, sender_id: int) -> bool:
    return db.query(TeamRequest).filter(
        TeamRequest.project_id == project_id,
        TeamRequest.sender_id == sender_id,
        TeamRequest.status == "pending"
    ).first() is not None


def get_project_members(db: Session, project_id: int) -> list[ProjectMember]:
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


def add_project_member(db: Session, project_id: int, user_id: int, role: str = "member") -> ProjectMember:
    db_member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def is_member(db: Session, project_id: int, user_id: int) -> bool:
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first() is not None


def create_skill(db: Session, skill: SkillCreate) -> Skill:
    db_skill = Skill(name=skill.name, description=skill.description)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


def get_skills(db: Session) -> list[Skill]:
    return db.query(Skill).all()


def get_skill(db: Session, skill_id: int) -> Optional[Skill]:
    return db.query(Skill).filter(Skill.id == skill_id).first()


def add_user_skill(db: Session, user_id: int, skill_id: int, level: str = "beginner") -> UserSkill:
    db_user_skill = UserSkill(user_id=user_id, skill_id=skill_id, level=level)
    db.add(db_user_skill)
    db.commit()
    db.refresh(db_user_skill)
    return db_user_skill


def get_user_skills(db: Session, user_id: int) -> list[UserSkill]:
    return db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
