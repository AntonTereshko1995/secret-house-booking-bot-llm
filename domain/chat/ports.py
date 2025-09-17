"""
Chat domain ports (interfaces)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from uuid import UUID

from .entities import ChatSession


class ChatRepository(ABC):
    """Port for chat repository"""

    @abstractmethod
    async def create(self, chat_session: ChatSession) -> ChatSession:
        """Create a new chat session"""
        pass

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> ChatSession | None:
        """Get chat session by ID"""
        pass

    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> ChatSession | None:
        """Get chat session by Telegram chat ID"""
        pass

    @abstractmethod
    async def update(self, chat_session: ChatSession) -> ChatSession:
        """Update chat session"""
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete chat session"""
        pass

    @abstractmethod
    async def save_state(self, chat_id: int, state_data: Dict[str, Any]) -> None:
        """Save LangGraph state for a chat session"""
        pass

    @abstractmethod
    async def get_state(self, chat_id: int) -> Dict[str, Any] | None:
        """Get LangGraph state for a chat session"""
        pass

    @abstractmethod
    async def clear_state(self, chat_id: int) -> None:
        """Clear LangGraph state for a chat session"""
        pass

    @abstractmethod
    async def update_conversation_context(
        self, chat_id: int, context: Dict[str, Any]
    ) -> None:
        """Update conversation context for a chat session"""
        pass

    @abstractmethod
    async def get_active_sessions_by_user(self, user_id: UUID) -> list[ChatSession]:
        """Get all active chat sessions for a user"""
        pass

    @abstractmethod
    async def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up inactive sessions older than specified hours"""
        pass