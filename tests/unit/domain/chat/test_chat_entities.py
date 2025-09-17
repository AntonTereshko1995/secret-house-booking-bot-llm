"""Tests for chat domain entities"""

import pytest
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any

from domain.chat.entities import (
    ChatSession, 
    ConversationContext,
    SessionCreateRequest,
    SessionUpdateRequest
)


class TestConversationContext:
    """Test ConversationContext entity"""

    def test_create_empty_conversation_context(self):
        """Test creating empty conversation context"""
        context = ConversationContext()
        
        assert context.messages == []
        assert context.metadata == {}
        assert context.intent is None
        assert context.current_state is None

    def test_create_conversation_context_with_data(self):
        """Test creating conversation context with data"""
        messages = [{"role": "user", "content": "Hello"}]
        metadata = {"session_id": "123", "flow": "booking"}
        
        context = ConversationContext(
            messages=messages,
            metadata=metadata,
            intent="booking",
            current_state="waiting_for_dates"
        )
        
        assert context.messages == messages
        assert context.metadata == metadata
        assert context.intent == "booking"
        assert context.current_state == "waiting_for_dates"

    def test_conversation_context_serialization(self):
        """Test ConversationContext serialization"""
        context = ConversationContext(
            messages=[{"role": "user", "content": "Test message"}],
            metadata={"key": "value"},
            intent="test_intent"
        )
        
        data = context.model_dump()
        assert data["messages"] == [{"role": "user", "content": "Test message"}]
        assert data["metadata"] == {"key": "value"}
        assert data["intent"] == "test_intent"
        assert data["current_state"] is None

    def test_conversation_context_deserialization(self):
        """Test ConversationContext deserialization"""
        data = {
            "messages": [{"role": "assistant", "content": "How can I help?"}],
            "metadata": {"flow": "faq"},
            "intent": "faq",
            "current_state": "ready"
        }
        
        context = ConversationContext.model_validate(data)
        assert len(context.messages) == 1
        assert context.messages[0]["role"] == "assistant"
        assert context.metadata["flow"] == "faq"
        assert context.intent == "faq"
        assert context.current_state == "ready"


class TestSessionCreateRequest:
    """Test SessionCreateRequest entity"""

    def test_create_session_request_minimal(self):
        """Test creating session request with minimal data"""
        request = SessionCreateRequest(chat_id=123456)
        
        assert request.chat_id == 123456
        assert request.user_id is None
        assert request.session_type == "user"  # Default value

    def test_create_session_request_full(self):
        """Test creating session request with all data"""
        user_id = uuid4()
        request = SessionCreateRequest(
            chat_id=123456,
            user_id=user_id,
            session_type="group"
        )
        
        assert request.chat_id == 123456
        assert request.user_id == user_id
        assert request.session_type == "group"

    def test_session_create_request_validation(self):
        """Test SessionCreateRequest validation"""
        with pytest.raises(ValueError):
            SessionCreateRequest(chat_id=0)  # chat_id must be non-zero


class TestSessionUpdateRequest:
    """Test SessionUpdateRequest entity"""

    def test_create_session_update_request(self):
        """Test creating session update request"""
        state_data = {"key": "value", "step": 1}
        context_data = {"intent": "booking"}
        
        request = SessionUpdateRequest(
            state_data=state_data,
            conversation_context=context_data,
            is_active=False
        )
        
        assert request.state_data == state_data
        assert request.conversation_context == context_data
        assert request.is_active is False

    def test_session_update_request_optional_fields(self):
        """Test session update request with optional fields"""
        request = SessionUpdateRequest()
        
        assert request.state_data is None
        assert request.conversation_context is None
        assert request.is_active is None


class TestChatSession:
    """Test ChatSession entity"""

    def test_create_chat_session_minimal(self):
        """Test creating chat session with minimal data"""
        session = ChatSession(chat_id=123456)
        
        assert session.chat_id == 123456
        assert session.user_id is None
        assert session.session_type == "user"
        assert session.state_data == {}
        assert isinstance(session.conversation_context, dict)
        assert session.is_active is True
        assert isinstance(session.last_activity_at, datetime)
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)

    def test_create_chat_session_full(self):
        """Test creating chat session with all data"""
        session_id = uuid4()
        user_id = uuid4()
        state_data = {"current_step": "payment", "booking_id": "123"}
        context = ConversationContext(
            messages=[{"role": "user", "content": "I want to book"}],
            intent="booking"
        )
        created_at = datetime.utcnow()
        
        session = ChatSession(
            id=session_id,
            chat_id=123456,
            user_id=user_id,
            session_type="private",
            state_data=state_data,
            conversation_context=context.model_dump(),
            is_active=True,
            last_activity_at=created_at,
            created_at=created_at,
            updated_at=created_at
        )
        
        assert session.id == session_id
        assert session.chat_id == 123456
        assert session.user_id == user_id
        assert session.session_type == "private"
        assert session.state_data == state_data
        assert session.conversation_context["intent"] == "booking"
        assert session.is_active is True
        assert session.last_activity_at == created_at

    def test_chat_session_defaults(self):
        """Test chat session default values"""
        session = ChatSession(chat_id=123456)
        
        assert session.session_type == "user"
        assert session.state_data == {}
        assert session.is_active is True
        assert session.id is not None
        assert session.created_at is not None
        assert session.updated_at is not None
        assert session.last_activity_at is not None

    def test_chat_session_validation(self):
        """Test chat session validation"""
        with pytest.raises(ValueError):
            ChatSession(chat_id=0)  # chat_id must be non-zero

    def test_chat_session_serialization(self):
        """Test ChatSession serialization"""
        user_id = uuid4()
        session = ChatSession(
            chat_id=123456,
            user_id=user_id,
            session_type="group",
            state_data={"step": 1},
            conversation_context={"intent": "faq"}
        )
        
        data = session.model_dump()
        assert data["chat_id"] == 123456
        assert data["user_id"] == str(user_id)
        assert data["session_type"] == "group"
        assert data["state_data"] == {"step": 1}
        assert data["conversation_context"] == {"intent": "faq"}

    def test_chat_session_deserialization(self):
        """Test ChatSession deserialization"""
        user_id = uuid4()
        data = {
            "chat_id": 123456,
            "user_id": user_id,
            "session_type": "private",
            "state_data": {"current_flow": "booking"},
            "conversation_context": {
                "messages": [],
                "metadata": {},
                "intent": "booking",
                "current_state": None
            },
            "is_active": True
        }
        
        session = ChatSession.model_validate(data)
        assert session.chat_id == 123456
        assert session.user_id == user_id
        assert session.session_type == "private"
        assert session.state_data["current_flow"] == "booking"
        assert session.conversation_context["intent"] == "booking"

    def test_chat_session_update_activity(self):
        """Test updating chat session activity"""
        session = ChatSession(chat_id=123456)
        original_activity = session.last_activity_at
        
        # Simulate time passing
        import time
        time.sleep(0.001)
        
        new_activity = datetime.utcnow()
        session.last_activity_at = new_activity
        
        assert session.last_activity_at > original_activity

    def test_chat_session_state_data_updates(self):
        """Test updating chat session state data"""
        session = ChatSession(
            chat_id=123456,
            state_data={"step": 1, "data": "initial"}
        )
        
        # Update state data
        session.state_data["step"] = 2
        session.state_data["new_field"] = "added"
        
        assert session.state_data["step"] == 2
        assert session.state_data["data"] == "initial"
        assert session.state_data["new_field"] == "added"

    def test_chat_session_conversation_context_updates(self):
        """Test updating conversation context"""
        session = ChatSession(
            chat_id=123456,
            conversation_context={"messages": [], "intent": None}
        )
        
        # Add message to context
        session.conversation_context["messages"].append({
            "role": "user",
            "content": "Hello",
            "timestamp": datetime.utcnow().isoformat()
        })
        session.conversation_context["intent"] = "greeting"
        
        assert len(session.conversation_context["messages"]) == 1
        assert session.conversation_context["intent"] == "greeting"