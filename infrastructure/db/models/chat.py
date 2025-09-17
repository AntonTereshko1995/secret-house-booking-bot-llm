"""
Chat session database model

SQLAlchemy model for chat sessions and LangGraph state persistence.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class ChatSessionModel(BaseModel):
    """Chat session model for LangGraph state persistence"""
    __tablename__ = "chat_sessions"
    
    # Session identification
    thread_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Thread ID in format {chat_id}:{user_id}"
    )
    
    chat_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Telegram chat ID"
    )
    
    # User relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to user record"
    )
    
    telegram_user_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Direct Telegram user ID for quick lookups"
    )
    
    # LangGraph state management
    current_intent = Column(
        String(50),
        nullable=True,
        comment="Current conversation intent: booking, faq, pricing, etc."
    )
    
    state_data = Column(
        JSON,
        nullable=True,
        comment="Complete LangGraph state data as JSON"
    )
    
    conversation_context = Column(
        JSON,
        nullable=True,
        comment="Conversation history and context for LLM continuity"
    )
    
    # Session metadata
    last_message_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp of last message in session"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the session is currently active"
    )
    
    session_end_reason = Column(
        String(100),
        nullable=True,
        comment="Reason session ended: completed, timeout, cancelled"
    )
    
    # Relationships
    user = relationship(
        "UserModel",
        back_populates="chat_sessions",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<ChatSessionModel(id={self.id}, thread_id={self.thread_id}, "
            f"intent={self.current_intent}, active={self.is_active})>"
        )