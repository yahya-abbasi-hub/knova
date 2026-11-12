import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemberInvite(BaseModel):
    user_email: str
    role: str = "viewer"


class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberRoleUpdate(BaseModel):
    role: str