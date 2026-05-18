from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberResponse
from src import crud
from src.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new project."""
    return crud.create_project(db, project, owner_id=current_user.id)


@router.get("/", response_model=list[ProjectResponse])
def list_projects(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all projects. Optionally filter by status (open/closed)."""
    return crud.get_projects(db, skip=skip, limit=limit, status_filter=status)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a project by ID."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Update a project. Only the project owner can update."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    return crud.update_project(db, project_id, project_update)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete a project. Only the project owner can delete."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    crud.delete_project(db, project_id)


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def get_project_members(project_id: int, db: Session = Depends(get_db)):
    """Get all members of a project."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_project_members(db, project_id)
