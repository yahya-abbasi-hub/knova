import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.models.document import Document
from backend.core.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE_BYTES
from backend.core.exceptions import ValidationError, NotFoundError, PermissionDeniedError
from backend.services import workspace_service
from backend.core.permissions import Role
from backend.models.chunk import Chunk

UPLOAD_DIR = Path("data/raw")


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def upload_document(
    db: Session,
    owner_id: uuid.UUID,
    workspace_id: uuid.UUID,
    file: UploadFile,
) -> Document:
    # 1. Confirm the workspace exists and belongs to this user
    workspace_service.require_permission(db, workspace_id, owner_id, "upload")

    # 2. Validate file type
    extension = _get_extension(file.filename)
    if extension not in ALLOWED_FILE_TYPES:
        raise ValidationError(
            f"Unsupported file type '.{extension}'. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
        )

    # 3. Read file content and validate size
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise ValidationError("File is too large (max 20MB)")

    # 4. Generate a safe, unique filename for disk storage
    document_id = uuid.uuid4()
    safe_filename = f"{document_id}.{extension}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(content)

    # 5. Create the database record
    document = Document(
        id=document_id,
        workspace_id=workspace_id,
        owner_id=owner_id,
        filename=file.filename,          # original name, for display
        file_type=extension,
        file_path=str(file_path),        # where it actually lives
        file_size_bytes=len(content),
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, owner_id: uuid.UUID, workspace_id: uuid.UUID) -> list[Document]:
    workspace_service.require_permission(db, workspace_id, owner_id, "view")
    return db.query(Document).filter(Document.workspace_id == workspace_id).all()
def delete_document(db, owner_id, workspace_id, document_id):
    workspace_service.require_permission(db, workspace_id, owner_id, "delete_document")

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.workspace_id == workspace_id,
    ).first()

    if document is None:
        raise NotFoundError("Document not found")

    # Delete chunks from Qdrant first
    from backend.rag.retrieval.vector_store import delete_chunks_by_document
    delete_chunks_by_document(document_id)

    # Delete the physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete the database record (Chunk rows will cascade if we set that up,
    # otherwise delete them explicitly first)
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    db.delete(document)
    db.commit()