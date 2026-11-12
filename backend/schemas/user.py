import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    """What the client sends when registering a new user."""
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    """What the client sends when logging in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """What we send back to the client — never includes the password."""
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """The response after successful login/register."""
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str | None = None  # only included in development mode, see note below


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str