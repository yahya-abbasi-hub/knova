import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkspaceCreate(BaseModel):
    """What the client sends to create a new workspace."""
    name: str
    description: str | None = None


class WorkspaceResponse(BaseModel):
    """What we send back to the client."""
    id: uuid.UUID
    name: str
    description: str | None
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)