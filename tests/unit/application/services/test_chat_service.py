"""Tests for ChatService"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any

from domain.chat.entities import ChatSession, ConversationContext
from application.services.chat_service import ChatService


class TestChatService:
    """Test ChatService"""

    @pytest.fixture
    def mock_chat_repository(self):
        """Mock chat repository"""
        return AsyncMock()

    @pytest.fixture
    def chat_service(self, mock_chat_repository):
        """ChatService instance with mocked repository"""
        return ChatService(mock_chat_repository)

    @pytest.fixture
    def sample_chat_session(self):
        """Sample chat session entity"""
        return ChatSession(
            id=uuid4(),
            chat_id=123456,
            user_id=uuid4(),
            session_type="user",
            state_data={"step": 1, "flow": "booking"},
            conversation_context={
                "messages": [],
                "metadata": {},
                "intent": "booking",
                "current_state": None
            },
            is_active=True,
            last_activity_at=datetime.utcnow()
        )

    async def test_create_chat_session(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test creating a chat session"""
        # Setup mock
        mock_chat_repository.create.return_value = sample_chat_session

        # Execute
        result = await chat_service.create_chat_session(sample_chat_session)

        # Verify
        assert result == sample_chat_session
        mock_chat_repository.create.assert_called_once_with(sample_chat_session)

    async def test_get_session_by_id(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test getting session by ID"""
        # Setup mock
        mock_chat_repository.get_by_id.return_value = sample_chat_session

        # Execute
        result = await chat_service.get_session_by_id(sample_chat_session.id)

        # Verify
        assert result == sample_chat_session
        mock_chat_repository.get_by_id.assert_called_once_with(sample_chat_session.id)

    async def test_get_session_by_chat_id(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test getting session by chat ID"""
        # Setup mock
        mock_chat_repository.get_by_chat_id.return_value = sample_chat_session

        # Execute
        result = await chat_service.get_session_by_chat_id(123456)

        # Verify
        assert result == sample_chat_session
        mock_chat_repository.get_by_chat_id.assert_called_once_with(123456)

    async def test_update_session(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test updating a session"""
        # Setup mock
        mock_chat_repository.update.return_value = sample_chat_session

        # Execute
        result = await chat_service.update_session(sample_chat_session)

        # Verify
        assert result == sample_chat_session
        mock_chat_repository.update.assert_called_once_with(sample_chat_session)

    async def test_save_langgraph_state(self, chat_service, mock_chat_repository):
        """Test saving LangGraph state"""
        # Setup
        chat_id = 123456
        state_data = {"current_step": "payment", "booking_data": {"date": "2024-01-01"}}

        # Execute
        await chat_service.save_langgraph_state(chat_id, state_data)

        # Verify
        mock_chat_repository.save_state.assert_called_once_with(chat_id, state_data)

    async def test_get_langgraph_state(self, chat_service, mock_chat_repository):
        """Test getting LangGraph state"""
        # Setup
        chat_id = 123456
        expected_state = {"current_step": "booking", "data": {"guests": 2}}
        mock_chat_repository.get_state.return_value = expected_state

        # Execute
        result = await chat_service.get_langgraph_state(chat_id)

        # Verify
        assert result == expected_state
        mock_chat_repository.get_state.assert_called_once_with(chat_id)

    async def test_clear_langgraph_state(self, chat_service, mock_chat_repository):
        """Test clearing LangGraph state"""
        # Setup
        chat_id = 123456

        # Execute
        await chat_service.clear_langgraph_state(chat_id)

        # Verify
        mock_chat_repository.clear_state.assert_called_once_with(chat_id)

    async def test_update_conversation_context(self, chat_service, mock_chat_repository):
        """Test updating conversation context"""
        # Setup
        chat_id = 123456
        context = {"intent": "faq", "topic": "pricing"}

        # Execute
        await chat_service.update_conversation_context(chat_id, context)

        # Verify
        mock_chat_repository.update_conversation_context.assert_called_once_with(chat_id, context)

    async def test_get_user_active_sessions(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test getting user active sessions"""
        # Setup
        user_id = uuid4()
        sessions_list = [sample_chat_session]
        mock_chat_repository.get_active_sessions_by_user.return_value = sessions_list

        # Execute
        result = await chat_service.get_user_active_sessions(user_id)

        # Verify
        assert result == sessions_list
        mock_chat_repository.get_active_sessions_by_user.assert_called_once_with(user_id)

    async def test_cleanup_inactive_sessions(self, chat_service, mock_chat_repository):
        """Test cleanup inactive sessions"""
        # Setup
        mock_chat_repository.cleanup_inactive_sessions.return_value = 5

        # Execute
        result = await chat_service.cleanup_inactive_sessions(24)

        # Verify
        assert result == 5
        mock_chat_repository.cleanup_inactive_sessions.assert_called_once_with(24)

    async def test_initialize_or_get_session_existing(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test initializing or getting existing session when session exists"""
        # Setup
        chat_id = 123456
        user_id = uuid4()
        mock_chat_repository.get_by_chat_id.return_value = sample_chat_session
        mock_chat_repository.update.return_value = sample_chat_session

        # Execute
        result = await chat_service.initialize_or_get_session(chat_id, user_id)

        # Verify
        assert result == sample_chat_session
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)
        mock_chat_repository.update.assert_called_once()
        mock_chat_repository.create.assert_not_called()

    async def test_initialize_or_get_session_new(self, chat_service, mock_chat_repository):
        """Test initializing or getting session when session doesn't exist"""
        # Setup
        chat_id = 123456
        user_id = uuid4()
        mock_chat_repository.get_by_chat_id.return_value = None
        new_session = ChatSession(
            chat_id=chat_id,
            user_id=user_id,
            session_type="user",
            state_data={},
            conversation_context={}
        )
        mock_chat_repository.create.return_value = new_session

        # Execute
        result = await chat_service.initialize_or_get_session(chat_id, user_id, "user")

        # Verify
        assert result == new_session
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)
        mock_chat_repository.create.assert_called_once()
        mock_chat_repository.update.assert_not_called()

    async def test_end_session(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test ending a session"""
        # Setup
        chat_id = 123456
        mock_chat_repository.get_by_chat_id.return_value = sample_chat_session
        inactive_session = ChatSession(
            id=sample_chat_session.id,
            chat_id=sample_chat_session.chat_id,
            user_id=sample_chat_session.user_id,
            session_type=sample_chat_session.session_type,
            state_data=sample_chat_session.state_data,
            conversation_context=sample_chat_session.conversation_context,
            is_active=False
        )
        mock_chat_repository.update.return_value = inactive_session

        # Execute
        result = await chat_service.end_session(chat_id)

        # Verify
        assert result is True
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)
        mock_chat_repository.update.assert_called_once()
        mock_chat_repository.clear_state.assert_called_once_with(chat_id)

    async def test_end_session_not_found(self, chat_service, mock_chat_repository):
        """Test ending a session that doesn't exist"""
        # Setup
        chat_id = 123456
        mock_chat_repository.get_by_chat_id.return_value = None

        # Execute
        result = await chat_service.end_session(chat_id)

        # Verify
        assert result is False
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)
        mock_chat_repository.update.assert_not_called()
        mock_chat_repository.clear_state.assert_not_called()

    async def test_get_conversation_history(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test getting conversation history"""
        # Setup
        chat_id = 123456
        mock_chat_repository.get_by_chat_id.return_value = sample_chat_session

        # Execute
        result = await chat_service.get_conversation_history(chat_id)

        # Verify
        assert result == sample_chat_session.conversation_context
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)

    async def test_get_conversation_history_no_session(self, chat_service, mock_chat_repository):
        """Test getting conversation history when no session exists"""
        # Setup
        chat_id = 123456
        mock_chat_repository.get_by_chat_id.return_value = None

        # Execute
        result = await chat_service.get_conversation_history(chat_id)

        # Verify
        assert result == {}
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)

    async def test_add_message_to_history_existing_session(self, chat_service, mock_chat_repository, sample_chat_session):
        """Test adding message to history for existing session"""
        # Setup
        chat_id = 123456
        message = "Hello, I want to book a room"
        role = "user"
        metadata = {"source": "telegram"}
        
        # Ensure conversation_context has messages array
        sample_chat_session.conversation_context = {"messages": []}
        mock_chat_repository.get_by_chat_id.return_value = sample_chat_session

        # Execute
        await chat_service.add_message_to_history(chat_id, message, role, metadata)

        # Verify
        mock_chat_repository.get_by_chat_id.assert_called_once_with(chat_id)
        mock_chat_repository.update_conversation_context.assert_called_once()
        
        # Check the updated context
        call_args = mock_chat_repository.update_conversation_context.call_args
        updated_context = call_args[0][1]
        assert len(updated_context["messages"]) == 1
        assert updated_context["messages"][0]["role"] == role
        assert updated_context["messages"][0]["content"] == message
        assert updated_context["messages"][0]["metadata"] == metadata

    async def test_add_message_to_history_new_session(self, chat_service, mock_chat_repository):
        """Test adding message to history when no session exists"""
        # Setup
        chat_id = 123456
        message = "Hello"
        
        # First call returns None (no session), second call returns new session
        new_session = ChatSession(
            chat_id=chat_id,
            conversation_context={"messages": []}
        )
        mock_chat_repository.get_by_chat_id.side_effect = [None, new_session]
        mock_chat_repository.create.return_value = new_session

        # Execute
        await chat_service.add_message_to_history(chat_id, message)

        # Verify
        assert mock_chat_repository.get_by_chat_id.call_count == 2
        mock_chat_repository.create.assert_called_once()
        mock_chat_repository.update_conversation_context.assert_called_once()

    async def test_add_message_to_history_message_limit(self, chat_service, mock_chat_repository):
        """Test message history limit (keep only last 50 messages)"""
        # Setup
        chat_id = 123456
        
        # Create session with 50 messages
        existing_messages = [{"role": "user", "content": f"Message {i}"} for i in range(50)]
        session = ChatSession(
            chat_id=chat_id,
            conversation_context={"messages": existing_messages}
        )
        mock_chat_repository.get_by_chat_id.return_value = session

        # Execute - add one more message
        await chat_service.add_message_to_history(chat_id, "New message")

        # Verify that only last 50 messages are kept
        call_args = mock_chat_repository.update_conversation_context.call_args
        updated_context = call_args[0][1]
        assert len(updated_context["messages"]) == 50
        assert updated_context["messages"][-1]["content"] == "New message"
        # First message should be "Message 1" (Message 0 was removed)
        assert "Message 1" in updated_context["messages"][0]["content"]