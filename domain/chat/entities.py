"""
Chat conversation domain entities

Domain models for chat sessions and LangGraph state persistence.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ConversationContext(BaseModel):
    """Conversation context for LLM continuity"""
    
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Conversation history with role and content"
    )
    user_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User preferences learned during conversation"
    )
    session_start: datetime = Field(
        default_factory=datetime.now,
        description="When the conversation session started"
    )
    total_messages: int = Field(default=0, description="Total messages in session")
    
    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    """Chat session domain entity for LangGraph state persistence"""
    
    id: UUID = Field(default_factory=uuid4, description="Internal session ID")
    thread_id: str = Field(..., description="Thread ID in format {chat_id}:{user_id}")
    chat_id: int = Field(..., description="Telegram chat ID")
    user_id: UUID = Field(..., description="Reference to User ID")
    telegram_user_id: int = Field(..., description="Telegram user ID for quick lookup")
    
    # LangGraph state management
    current_intent: Optional[str] = Field(None, description="Current conversation intent")
    state_data: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Complete LangGraph state data"
    )
    conversation_context: Optional[ConversationContext] = Field(
        None, 
        description="Conversation history and context for LLM"
    )
    
    # Session metadata
    last_message_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of last message"
    )
    is_active: bool = Field(default=True, description="Whether session is active")
    session_end_reason: Optional[str] = Field(
        None, 
        description="Reason session ended: completed, timeout, cancelled"
    )
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SessionCreateRequest(BaseModel):
    """Request to create a new chat session"""
    
    thread_id: str = Field(..., description="Thread ID in format {chat_id}:{user_id}")
    chat_id: int = Field(..., description="Telegram chat ID")
    telegram_user_id: int = Field(..., description="Telegram user ID")
    current_intent: Optional[str] = Field(None, description="Initial conversation intent")
    state_data: Dict[str, Any] = Field(default_factory=dict, description="Initial state data")


class SessionUpdateRequest(BaseModel):
    """Request to update chat session state"""
    
    current_intent: Optional[str] = Field(None, description="Updated conversation intent")
    state_data: Optional[Dict[str, Any]] = Field(None, description="Updated state data")
    conversation_context: Optional[ConversationContext] = Field(None, description="Updated conversation context")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    session_end_reason: Optional[str] = Field(None, description="Reason for ending session")


class StateSnapshot(BaseModel):
    """Snapshot of LangGraph state for persistence"""
    
    thread_id: str = Field(..., description="Thread ID")
    intent: Optional[str] = Field(None, description="Current intent")
    context: Dict[str, Any] = Field(default_factory=dict, description="Booking context")
    reply: Optional[str] = Field(None, description="Last reply")
    await_input: Optional[bool] = Field(None, description="Whether awaiting user input")
    active_subgraph: Optional[str] = Field(None, description="Current active subgraph")
    faq_data: Optional[Dict[str, Any]] = Field(None, description="FAQ response data")
    faq_context: Optional[Dict[str, Any]] = Field(None, description="FAQ conversation context")
    
    class Config:
        from_attributes = True