import uuid

from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database.session import get_db, SessionLocal
from backend.api.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.document import DocumentResponse
from backend.services import document_service
from backend.ingestion.pipeline import process_document
from backend.models.chunk import Chunk
from backend.schemas.document import ChunkResponse

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["Documents"])


@router.post("/", response_model=DocumentResponse, status_code=201)
def upload_document(
    workspace_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = document_service.upload_document(db, current_user.id, workspace_id, file)
    background_tasks.add_task(process_document, document.id, SessionLocal)
    return document


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return document_service.list_documents(db, current_user.id, workspace_id)

@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def get_document_chunks(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Quick ownership check: confirm the workspace belongs to this user
    from backend.services import workspace_service
    workspace_service.get_workspace(db, current_user.id, workspace_id)

    return (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
        .all()
    )
@router.delete("/{document_id}", status_code=204)
def delete_document(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document_service.delete_document(db, current_user.id, workspace_id, document_id)