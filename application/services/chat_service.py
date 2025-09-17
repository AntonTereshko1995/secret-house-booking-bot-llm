"""
Chat service for managing chat sessions and LangGraph state
"""

from typing import Dict, Any, TYPE_CHECKING
from uuid import UUID

from domain.chat.entities import ChatSession, ConversationContext

if TYPE_CHECKING:
    from domain.chat.ports import ChatRepository


class ChatService:
    """Service for chat session and LangGraph state management"""

    def __init__(self, chat_repository: "ChatRepository"):
        self.chat_repository = chat_repository

    async def create_chat_session(self, chat_session: ChatSession) -> ChatSession:
        """Create a new chat session"""
        return await self.chat_repository.create(chat_session)

    async def get_session_by_id(self, session_id: UUID) -> ChatSession | None:
        """Get chat session by ID"""
        return await self.chat_repository.get_by_id(session_id)

    async def get_session_by_chat_id(self, chat_id: int) -> ChatSession | None:
        """Get chat session by Telegram chat ID"""
        return await self.chat_repository.get_by_chat_id(chat_id)

    async def update_session(self, chat_session: ChatSession) -> ChatSession:
        """Update chat session"""
        return await self.chat_repository.update(chat_session)

    async def save_langgraph_state(
        self, chat_id: int, state_data: Dict[str, Any]
    ) -> None:
        """Save LangGraph state for a chat session"""
        await self.chat_repository.save_state(chat_id, state_data)

    async def get_langgraph_state(self, chat_id: int) -> Dict[str, Any] | None:
        """Get LangGraph state for a chat session"""
        return await self.chat_repository.get_state(chat_id)

    async def clear_langgraph_state(self, chat_id: int) -> None:
        """Clear LangGraph state for a chat session"""
        await self.chat_repository.clear_state(chat_id)

    async def update_conversation_context(
        self, chat_id: int, context: Dict[str, Any]
    ) -> None:
        """Update conversation context for a chat session"""
        await self.chat_repository.update_conversation_context(chat_id, context)

    async def get_user_active_sessions(self, user_id: UUID) -> list[ChatSession]:
        """Get all active chat sessions for a user"""
        return await self.chat_repository.get_active_sessions_by_user(user_id)

    async def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up inactive sessions older than specified hours"""
        return await self.chat_repository.cleanup_inactive_sessions(max_age_hours)

    async def initialize_or_get_session(
        self, 
        chat_id: int, 
        user_id: UUID | None = None,
        session_type: str = "user"
    ) -> ChatSession:
        """Initialize a new chat session or get existing one"""
        existing_session = await self.chat_repository.get_by_chat_id(chat_id)
        
        if existing_session:
            # Update last activity and return existing session
            from datetime import datetime
            existing_session.last_activity_at = datetime.utcnow()
            return await self.chat_repository.update(existing_session)
        else:
            # Create new session
            from datetime import datetime
            
            new_session = ChatSession(
                chat_id=chat_id,
                user_id=user_id,
                session_type=session_type,
                state_data={},
                conversation_context=ConversationContext().model_dump(),
                is_active=True,
                last_activity_at=datetime.utcnow()
            )
            
            return await self.chat_repository.create(new_session)

    async def end_session(self, chat_id: int) -> bool:
        """End a chat session (soft delete)"""
        session = await self.chat_repository.get_by_chat_id(chat_id)
        if not session:
            return False
        
        session.is_active = False
        await self.chat_repository.update(session)
        await self.chat_repository.clear_state(chat_id)
        return True

    async def get_conversation_history(self, chat_id: int) -> Dict[str, Any]:
        """Get conversation history for a chat session"""
        session = await self.chat_repository.get_by_chat_id(chat_id)
        if not session or not session.conversation_context:
            return {}
        
        return session.conversation_context

    async def add_message_to_history(
        self, 
        chat_id: int, 
        message: str, 
        role: str = "user",
        metadata: Dict[str, Any] | None = None
    ) -> None:
        """Add a message to conversation history"""
        session = await self.chat_repository.get_by_chat_id(chat_id)
        if not session:
            # Create session if it doesn't exist
            session = await self.initialize_or_get_session(chat_id)
        
        context = session.conversation_context or {}
        if "messages" not in context:
            context["messages"] = []
        
        from datetime import datetime
        message_entry = {
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        context["messages"].append(message_entry)
        
        # Keep only last 50 messages to prevent unlimited growth
        if len(context["messages"]) > 50:
            context["messages"] = context["messages"][-50:]
        
        await self.chat_repository.update_conversation_context(chat_id, context)