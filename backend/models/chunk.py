import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.session import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)   # order within the document (0, 1, 2, ...)
    text = Column(String, nullable=False)
    char_count = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", backref="chunks")