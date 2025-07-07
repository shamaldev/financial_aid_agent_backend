from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# models.py
import uuid
from sqlalchemy.dialects.postgresql import UUID

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    
class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)  # Filename of the policy
    hash = Column(String, unique=True, nullable=False)  # Hash to prevent duplicates
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Track uploader
    file_path   = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(Integer, primary_key=True, nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id    = Column(UUID(as_uuid=True), nullable=False, index=True, default=uuid.uuid4)
    message    = Column(String, nullable=False)
    is_user    = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    chat_id     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    # policy_id   = Column(Integer, ForeignKey("policies.id"), nullable=False)
    created_at  = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()'),
        onupdate=text('now()')
    )
    
class EvaluationSession(Base):
    __tablename__ = "evaluation_sessions"
    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_name  = Column(String, nullable=False)
    doc_name          = Column(String, nullable=False)
    application_json  = Column(Text, nullable=False)
    created_at        = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    last_updated      = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    revisions         = relationship("EvaluationRevision", back_populates="session")

class EvaluationRevision(Base):
    __tablename__ = "evaluation_revisions"
    id              = Column(Integer, primary_key=True, nullable=False)
    session_id      = Column(UUID(as_uuid=True), ForeignKey("evaluation_sessions.id"), nullable=False)
    report          = Column(String, nullable=False)
    feedback        = Column(String, nullable=True)
    revision_number = Column(Integer, nullable=False)
    created_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    session         = relationship("EvaluationSession", back_populates="revisions")

