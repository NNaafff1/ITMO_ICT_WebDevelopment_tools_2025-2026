from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import TeamRequestCreate, TeamRequestResponse
from src import crud
from src.auth import get_current_user

router = APIRouter(prefix="/team-requests", tags=["Team Requests"])


@router.post("/", response_model=TeamRequestResponse, status_code=201)
def send_request(request: TeamRequestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Send a join request to a project."""
    project = crud.get_project(db, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot apply to your own project")
    if crud.is_member(db, request.project_id, current_user.id):
        raise HTTPException(status_code=400, detail="Already a member of this project")
    if crud.has_pending_request(db, request.project_id, current_user.id):
        raise HTTPException(status_code=400, detail="Already have a pending request for this project")
    return crud.create_team_request(db, request, sender_id=current_user.id)


@router.get("/my", response_model=list[TeamRequestResponse])
def my_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all requests sent by the current user."""
    return crud.get_requests_by_sender(db, current_user.id)


@router.get("/incoming", response_model=list[TeamRequestResponse])
def incoming_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all incoming requests for the current user's projects."""
    return crud.get_incoming_requests_for_user(db, current_user.id)


@router.put("/{request_id}/accept", response_model=TeamRequestResponse)
def accept_request(request_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Accept a team request. Only the project owner can accept."""
    req = crud.get_team_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    project = crud.get_project(db, req.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    crud.add_project_member(db, req.project_id, req.sender_id, role="member")
    return crud.update_request_status(db, request_id, "accepted")


@router.put("/{request_id}/reject", response_model=TeamRequestResponse)
def reject_request(request_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Reject a team request. Only the project owner can reject."""
    req = crud.get_team_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    project = crud.get_project(db, req.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    return crud.update_request_status(db, request_id, "rejected")
