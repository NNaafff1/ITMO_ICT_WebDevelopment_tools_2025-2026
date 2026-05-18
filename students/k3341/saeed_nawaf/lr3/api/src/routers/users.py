from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import UserResponse, UserUpdate
from src import crud
from src.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def list_users(skill: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users. Optionally filter by skill."""
    return crud.get_users(db, skip=skip, limit=limit, skill_filter=skill)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Update user profile. Only the account owner can update."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    updated = crud.update_user(db, user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete user account. Only the account owner can delete."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this account")
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
