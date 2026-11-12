import uuid

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class SourceCitation(BaseModel):
    document_id: uuid.UUID
    document_name: str
    chunk_index: int
    snippet: str  # short preview of the chunk text used


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    grounded: bool  # False if we couldn't find enough evidence to answer