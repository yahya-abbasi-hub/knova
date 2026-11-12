import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.api.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.workspace_member import MemberInvite, MemberResponse
from backend.services import workspace_service

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["Workspace Members"])


@router.get("/", response_model=list[MemberResponse])
def list_members(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return workspace_service.list_members(db, workspace_id, current_user.id)


@router.post("/", response_model=MemberResponse, status_code=201)
def invite_member(
    workspace_id: uuid.UUID,
    data: MemberInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = workspace_service.invite_member(
        db, workspace_id, current_user.id, data.user_email, data.role
    )
    user = db.query(User).filter(User.id == membership.user_id).first()
    return MemberResponse(
        id=membership.id, user_id=membership.user_id, user_email=user.email,
        role=membership.role, created_at=membership.created_at,
    )


@router.delete("/{user_id}", status_code=204)
def remove_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace_service.remove_member(db, workspace_id, current_user.id, user_id)