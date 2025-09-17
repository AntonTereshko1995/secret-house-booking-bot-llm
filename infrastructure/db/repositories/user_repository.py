"""
User repository implementation

Repository for user-specific database operations including
Telegram user management and profile operations.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from domain.user.entities import User, UserCreateRequest, UserUpdateRequest
from infrastructure.db.models.user import UserModel

from .base import BaseRepository

logger = get_logger(__name__)


class UserRepository(BaseRepository[User, UserModel]):
    """User repository for Telegram user management"""
    
    def __init__(self, session: AsyncSession):
        """Initialize user repository
        
        Args:
            session: Async SQLAlchemy session
        """
        super().__init__(session, UserModel)
    
    async def find_by_telegram_id(self, telegram_id: int) -> Optional[UserModel]:
        """Find user by Telegram ID
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User model instance or None if not found
        """
        try:
            stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                logger.debug(
                    "Found user by Telegram ID",
                    extra={"telegram_id": telegram_id, "user_id": str(user.id)}
                )
            
            return user
            
        except Exception as e:
            logger.error(
                f"Error finding user by Telegram ID: {e}",
                extra={"telegram_id": telegram_id}
            )
            raise
    
    async def create_from_telegram_user(self, user_request: UserCreateRequest) -> UserModel:
        """Create user from Telegram user data
        
        Args:
            user_request: User creation request with Telegram data
            
        Returns:
            Created user model instance
        """
        try:
            user_data = {
                "telegram_id": user_request.telegram_id,
                "username": user_request.username,
                "phone_number": user_request.phone_number,
                "language_code": user_request.language_code,
                "is_active": True
            }
            
            user = await self.create(user_data)
            
            logger.info(
                "Created user from Telegram data",
                extra={
                    "telegram_id": user_request.telegram_id,
                    "user_id": str(user.id),
                    "username": user_request.username
                }
            )
            
            return user
            
        except Exception as e:
            logger.error(
                f"Error creating user from Telegram data: {e}",
                extra={"telegram_id": user_request.telegram_id}
            )
            raise
    
    async def update_profile(
        self, 
        telegram_id: int, 
        update_request: UserUpdateRequest
    ) -> Optional[UserModel]:
        """Update user profile information
        
        Args:
            telegram_id: Telegram user ID
            update_request: User update request with new data
            
        Returns:
            Updated user model instance or None if not found
        """
        try:
            # Find user by Telegram ID
            user = await self.find_by_telegram_id(telegram_id)
            if not user:
                return None
            
            # Prepare update data (only non-None fields)
            update_data = {}
            if update_request.username is not None:
                update_data["username"] = update_request.username
            if update_request.phone_number is not None:
                update_data["phone_number"] = update_request.phone_number
            if update_request.language_code is not None:
                update_data["language_code"] = update_request.language_code
            if update_request.is_active is not None:
                update_data["is_active"] = update_request.is_active
            
            if not update_data:
                return user  # No updates to apply
            
            # Update user
            updated_user = await self.update(user.id, update_data)
            
            logger.info(
                "Updated user profile",
                extra={
                    "telegram_id": telegram_id,
                    "user_id": str(user.id),
                    "updates": update_data
                }
            )
            
            return updated_user
            
        except Exception as e:
            logger.error(
                f"Error updating user profile: {e}",
                extra={"telegram_id": telegram_id}
            )
            raise
    
    async def get_or_create_user(self, user_request: UserCreateRequest) -> UserModel:
        """Get existing user or create new one from Telegram data
        
        Args:
            user_request: User creation request with Telegram data
            
        Returns:
            Existing or newly created user model instance
        """
        try:
            # Try to find existing user
            existing_user = await self.find_by_telegram_id(user_request.telegram_id)
            
            if existing_user:
                logger.debug(
                    "Found existing user",
                    extra={
                        "telegram_id": user_request.telegram_id,
                        "user_id": str(existing_user.id)
                    }
                )
                return existing_user
            
            # Create new user
            new_user = await self.create_from_telegram_user(user_request)
            return new_user
            
        except Exception as e:
            logger.error(
                f"Error in get_or_create_user: {e}",
                extra={"telegram_id": user_request.telegram_id}
            )
            raise
    
    async def deactivate_user(self, telegram_id: int) -> bool:
        """Deactivate user account
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if user was deactivated, False if not found
        """
        try:
            user = await self.find_by_telegram_id(telegram_id)
            if not user:
                return False
            
            await self.update(user.id, {"is_active": False})
            
            logger.info(
                "Deactivated user account",
                extra={"telegram_id": telegram_id, "user_id": str(user.id)}
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error deactivating user: {e}",
                extra={"telegram_id": telegram_id}
            )
            raise
    
    def _to_domain_entity(self, db_user: UserModel) -> User:
        """Convert database model to domain entity
        
        Args:
            db_user: Database user model
            
        Returns:
            User domain entity
        """
        return User(
            id=db_user.id,
            telegram_id=db_user.telegram_id,
            username=db_user.username,
            phone_number=db_user.phone_number,
            language_code=db_user.language_code,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )