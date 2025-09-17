"""
Chat session repository implementation

Repository for chat session and LangGraph state persistence operations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from domain.chat.entities import ChatSession, ConversationContext, SessionCreateRequest
from infrastructure.db.models.chat import ChatSessionModel

from .base import BaseRepository

logger = get_logger(__name__)


class ChatRepository(BaseRepository[ChatSession, ChatSessionModel]):
    """Chat session repository for LangGraph state persistence"""
    
    def __init__(self, session: AsyncSession):
        """Initialize chat repository
        
        Args:
            session: Async SQLAlchemy session
        """
        super().__init__(session, ChatSessionModel)
    
    async def find_by_thread_id(self, thread_id: str) -> Optional[ChatSessionModel]:
        """Find chat session by thread ID
        
        Args:
            thread_id: Thread ID in format {chat_id}:{user_id}
            
        Returns:
            Chat session model instance or None if not found
        """
        try:
            stmt = select(ChatSessionModel).where(ChatSessionModel.thread_id == thread_id)
            result = await self.session.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                logger.debug(
                    "Found chat session by thread ID",
                    extra={"thread_id": thread_id, "session_id": str(session.id)}
                )
            
            return session
            
        except Exception as e:
            logger.error(
                f"Error finding chat session by thread ID: {e}",
                extra={"thread_id": thread_id}
            )
            raise
    
    async def find_active_sessions_by_user(self, telegram_user_id: int) -> List[ChatSessionModel]:
        """Find active chat sessions for a user
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            List of active chat session model instances
        """
        try:
            stmt = (
                select(ChatSessionModel)
                .where(
                    ChatSessionModel.telegram_user_id == telegram_user_id,
                    ChatSessionModel.is_active == True
                )
                .order_by(ChatSessionModel.last_message_at.desc())
            )
            result = await self.session.execute(stmt)
            sessions = list(result.scalars().all())
            
            logger.debug(
                "Found active sessions for user",
                extra={"telegram_user_id": telegram_user_id, "count": len(sessions)}
            )
            
            return sessions
            
        except Exception as e:
            logger.error(
                f"Error finding active sessions by user: {e}",
                extra={"telegram_user_id": telegram_user_id}
            )
            raise
    
    async def create_session(
        self, 
        session_request: SessionCreateRequest,
        user_id: UUID
    ) -> ChatSessionModel:
        """Create new chat session
        
        Args:
            session_request: Session creation request
            user_id: User UUID from database
            
        Returns:
            Created chat session model instance
        """
        try:
            session_data = {
                "thread_id": session_request.thread_id,
                "chat_id": session_request.chat_id,
                "user_id": user_id,
                "telegram_user_id": session_request.telegram_user_id,
                "current_intent": session_request.current_intent,
                "state_data": session_request.state_data,
                "conversation_context": None,  # Will be updated as conversation progresses
                "is_active": True
            }
            
            session = await self.create(session_data)
            
            logger.info(
                "Created chat session",
                extra={
                    "session_id": str(session.id),
                    "thread_id": session_request.thread_id,
                    "telegram_user_id": session_request.telegram_user_id
                }
            )
            
            return session
            
        except Exception as e:
            logger.error(
                f"Error creating chat session: {e}",
                extra={"thread_id": session_request.thread_id}
            )
            raise
    
    async def save_state(
        self, 
        thread_id: str, 
        state_data: Dict[str, Any],
        current_intent: Optional[str] = None
    ) -> Optional[ChatSessionModel]:
        """Save LangGraph state data
        
        Args:
            thread_id: Thread ID
            state_data: LangGraph state data to save
            current_intent: Optional current conversation intent
            
        Returns:
            Updated chat session model instance or None if not found
        """
        try:
            session = await self.find_by_thread_id(thread_id)
            if not session:
                logger.warning(
                    "Chat session not found for state save",
                    extra={"thread_id": thread_id}
                )
                return None
            
            update_data = {
                "state_data": state_data,
                "last_message_at": datetime.now()
            }
            
            if current_intent:
                update_data["current_intent"] = current_intent
            
            updated_session = await self.update(session.id, update_data)
            
            logger.debug(
                "Saved LangGraph state",
                extra={
                    "thread_id": thread_id,
                    "session_id": str(session.id),
                    "intent": current_intent
                }
            )
            
            return updated_session
            
        except Exception as e:
            logger.error(
                f"Error saving state: {e}",
                extra={"thread_id": thread_id}
            )
            raise
    
    async def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get LangGraph state data
        
        Args:
            thread_id: Thread ID
            
        Returns:
            LangGraph state data or None if not found
        """
        try:
            session = await self.find_by_thread_id(thread_id)
            if not session:
                return None
            
            logger.debug(
                "Retrieved LangGraph state",
                extra={"thread_id": thread_id, "session_id": str(session.id)}
            )
            
            return session.state_data
            
        except Exception as e:
            logger.error(
                f"Error getting state: {e}",
                extra={"thread_id": thread_id}
            )
            raise
    
    async def save_conversation_context(
        self, 
        thread_id: str, 
        context: ConversationContext
    ) -> Optional[ChatSessionModel]:
        """Save conversation context for LLM continuity
        
        Args:
            thread_id: Thread ID
            context: Conversation context to save
            
        Returns:
            Updated chat session model instance or None if not found
        """
        try:
            session = await self.find_by_thread_id(thread_id)
            if not session:
                return None
            
            context_data = context.dict() if context else None
            
            update_data = {
                "conversation_context": context_data,
                "last_message_at": datetime.now()
            }
            
            updated_session = await self.update(session.id, update_data)
            
            logger.debug(
                "Saved conversation context",
                extra={
                    "thread_id": thread_id,
                    "session_id": str(session.id),
                    "message_count": len(context.conversation_history) if context else 0
                }
            )
            
            return updated_session
            
        except Exception as e:
            logger.error(
                f"Error saving conversation context: {e}",
                extra={"thread_id": thread_id}
            )
            raise
    
    async def end_session(
        self, 
        thread_id: str, 
        reason: str = "completed"
    ) -> Optional[ChatSessionModel]:
        """End chat session
        
        Args:
            thread_id: Thread ID
            reason: Reason for ending session
            
        Returns:
            Updated chat session model instance or None if not found
        """
        try:
            session = await self.find_by_thread_id(thread_id)
            if not session:
                return None
            
            update_data = {
                "is_active": False,
                "session_end_reason": reason,
                "last_message_at": datetime.now()
            }
            
            updated_session = await self.update(session.id, update_data)
            
            logger.info(
                "Ended chat session",
                extra={
                    "thread_id": thread_id,
                    "session_id": str(session.id),
                    "reason": reason
                }
            )
            
            return updated_session
            
        except Exception as e:
            logger.error(
                f"Error ending session: {e}",
                extra={"thread_id": thread_id, "reason": reason}
            )
            raise
    
    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old inactive sessions
        
        Args:
            days_old: Number of days after which to clean up sessions
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            stmt = (
                select(ChatSessionModel)
                .where(
                    ChatSessionModel.is_active == False,
                    ChatSessionModel.updated_at < cutoff_date
                )
            )
            result = await self.session.execute(stmt)
            old_sessions = list(result.scalars().all())
            
            cleanup_count = 0
            for session in old_sessions:
                await self.delete(session.id)
                cleanup_count += 1
            
            await self.session.commit()
            
            logger.info(
                "Cleaned up old chat sessions",
                extra={"cleanup_count": cleanup_count, "days_old": days_old}
            )
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            raise
    
    def _to_domain_entity(self, db_session: ChatSessionModel) -> ChatSession:
        """Convert database model to domain entity
        
        Args:
            db_session: Database chat session model
            
        Returns:
            ChatSession domain entity
        """
        # Convert conversation_context JSON back to ConversationContext if present
        conversation_context = None
        if db_session.conversation_context:
            conversation_context = ConversationContext(**db_session.conversation_context)
        
        return ChatSession(
            id=db_session.id,
            thread_id=db_session.thread_id,
            chat_id=db_session.chat_id,
            user_id=db_session.user_id,
            telegram_user_id=db_session.telegram_user_id,
            current_intent=db_session.current_intent,
            state_data=db_session.state_data or {},
            conversation_context=conversation_context,
            last_message_at=db_session.last_message_at,
            is_active=db_session.is_active,
            session_end_reason=db_session.session_end_reason,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at
        )