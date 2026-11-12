import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)        # e.g. "pdf", "docx", "txt"
    file_path = Column(String, nullable=False)         # where it's stored on disk
    file_size_bytes = Column(Integer, nullable=True)

    status = Column(String, default="uploaded", nullable=False)
    # status values: uploaded -> processing -> ready / failed

    page_count = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)      # populated if status == "failed"

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", backref="documents")
    owner = relationship("User", backref="documents")