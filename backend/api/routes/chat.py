import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.api.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services import chat_service

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["Chat"])


@router.post("/ask", response_model=ChatResponse)
def ask(
    workspace_id: uuid.UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.ask_question(db, current_user.id, workspace_id, request.question)