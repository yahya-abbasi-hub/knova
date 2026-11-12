import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    filename: str
    file_type: str
    file_size_bytes: int | None
    status: str
    page_count: int | None
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
class ChunkResponse(BaseModel):
    id: uuid.UUID
    chunk_index: int
    text: str
    char_count: int

    model_config = ConfigDict(from_attributes=True)