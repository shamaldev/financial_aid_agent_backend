from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal, Optional, List
import uuid

class UserCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr #ensures email is valid in format
    password: str

class Userout(BaseModel):
    id: int
    email : EmailStr
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class UserLogin(BaseModel):
    email : EmailStr
    password : str
class ProcessingResult(BaseModel):
    """
    Response schema for PDF processing endpoint.
    """
    document_name: str
    report: str
    evaluation_id: int
    status: Optional[str] = None  # Optional, only included in feedback revision workflow

    class Config:
        from_attributes = True

class PolicyUploadResult(BaseModel):
    uploaded: List[str]
    skipped: List[str]

class ChatSessionMeta(BaseModel):
    chat_id: uuid.UUID
    # policy_id: int
    # policy_name: str
    created_at: datetime
    last_updated: datetime

class ChatMessageOut(BaseModel):
    content: str
    role: Literal["user", "assistant"]
    created_at: datetime

class ChatListResponse(BaseModel):
    sessions: List[ChatSessionMeta]

class ChatHistoryResponse(BaseModel):
    chat_id: uuid.UUID
    messages: List[ChatMessageOut]

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[uuid.UUID] = None

class ChatResponse(BaseModel):
    response: str
    chat_id: uuid.UUID

class PolicyMeta(BaseModel):
    id:   int
    name: str
class EvalSessionMeta(BaseModel):
    id: uuid.UUID
    application_name: str
    doc_name: str
    created_at: datetime
    last_updated: datetime
class EvalRevisionOut(BaseModel):
    id: int
    report: str
    feedback: Optional[str]
    revision_number: int
    created_at: datetime
class EvalSessionListResponse(BaseModel):
    sessions: List[EvalSessionMeta]

class EvalRevisionListResponse(BaseModel):
    session_id: uuid.UUID
    revisions: List[EvalRevisionOut]

class UploadRequest(BaseModel):
    feedback: Optional[str] = None
    evaluation_id: Optional[uuid.UUID] = None

class UploadResponse(BaseModel):
    session_id: uuid.UUID
    report: str
    revision_number: int
    status: str
    query_response: Optional[str] = None

