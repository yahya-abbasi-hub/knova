import uuid

from sqlalchemy.orm import Session

from backend.models.workspace import Workspace
from backend.models.workspace_member import WorkspaceMember
from backend.schemas.workspace import WorkspaceCreate
from backend.core.exceptions import NotFoundError, PermissionDeniedError
from backend.core.permissions import Role, role_has_permission
from backend.models.user import User
from backend.schemas.workspace_member import MemberResponse

def create_workspace(db: Session, owner_id: uuid.UUID, data: WorkspaceCreate) -> Workspace:
    workspace = Workspace(
        name=data.name,
        description=data.description,
        owner_id=owner_id,
    )
    db.add(workspace)
    db.flush()  # get workspace.id before creating the membership row

    membership = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=owner_id,
        role=Role.OWNER.value,
    )
    db.add(membership)

    db.commit()
    db.refresh(workspace)
    return workspace


def get_user_role(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID) -> str | None:
    """Returns the user's role in a workspace, or None if they're not a member at all."""
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )
    return membership.role if membership else None


def require_permission(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID, permission: str):
    """
    Checks whether a user has a specific permission in a workspace.
    Raises NotFoundError if the workspace doesn't exist, PermissionDeniedError
    if the user isn't a member or their role lacks the permission.
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFoundError("Workspace not found")

    role = get_user_role(db, workspace_id, user_id)
    if role is None:
        raise PermissionDeniedError("You are not a member of this workspace")

    if not role_has_permission(role, permission):
        raise PermissionDeniedError(f"Your role ({role}) does not have '{permission}' permission")

    return workspace


def list_workspaces(db: Session, user_id: uuid.UUID) -> list[Workspace]:
    """Lists all workspaces the user is a MEMBER of (not just ones they own)."""
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user_id).all()
    workspace_ids = [m.workspace_id for m in memberships]
    return db.query(Workspace).filter(Workspace.id.in_(workspace_ids)).all()


def get_workspace(db: Session, user_id: uuid.UUID, workspace_id: uuid.UUID) -> Workspace:
    return require_permission(db, workspace_id, user_id, "view")


def delete_workspace(db: Session, user_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
    workspace = require_permission(db, workspace_id, user_id, "delete_workspace")
    db.delete(workspace)
    db.commit()



def list_members(db: Session, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID) -> list[MemberResponse]:
    require_permission(db, workspace_id, requesting_user_id, "view")

    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    result = []
    for m in memberships:
        user = db.query(User).filter(User.id == m.user_id).first()
        result.append(MemberResponse(
            id=m.id, user_id=m.user_id, user_email=user.email,
            role=m.role, created_at=m.created_at,
        ))
    return result


def invite_member(db: Session, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID, user_email: str, role: str):
    require_permission(db, workspace_id, requesting_user_id, "manage_members")

    target_user = db.query(User).filter(User.email == user_email).first()
    if target_user is None:
        raise NotFoundError("No user found with that email")

    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target_user.id,
    ).first()
    if existing:
        raise PermissionDeniedError("This user is already a member of the workspace")

    membership = WorkspaceMember(workspace_id=workspace_id, user_id=target_user.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def remove_member(db: Session, workspace_id: uuid.UUID, requesting_user_id: uuid.UUID, target_user_id: uuid.UUID):
    require_permission(db, workspace_id, requesting_user_id, "manage_members")

    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target_user_id,
    ).first()
    if membership is None:
        raise NotFoundError("This user is not a member of the workspace")
    if membership.role == Role.OWNER.value:
        raise PermissionDeniedError("Cannot remove the workspace owner")

    db.delete(membership)
    db.commit()