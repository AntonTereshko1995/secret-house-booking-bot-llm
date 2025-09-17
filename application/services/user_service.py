"""
User service for managing user operations
"""

from uuid import UUID
from typing import TYPE_CHECKING

from domain.user.entities import User

if TYPE_CHECKING:
    from domain.user.ports import UserRepository


class UserService:
    """Service for user management operations"""

    def __init__(self, user_repository: "UserRepository"):
        self.user_repository = user_repository

    async def create_user(self, user: User) -> User:
        """Create a new user"""
        return await self.user_repository.create(user)

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID"""
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID"""
        return await self.user_repository.get_by_telegram_id(telegram_id)

    async def update_user(self, user: User) -> User:
        """Update user information"""
        return await self.user_repository.update(user)

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate a user (soft delete)"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        await self.user_repository.update(user)
        return True

    async def find_user_by_username(self, username: str) -> User | None:
        """Find user by username"""
        return await self.user_repository.find_by_username(username)

    async def get_all_users(self) -> list[User]:
        """Get all users (admin operation)"""
        return await self.user_repository.get_all()

    async def register_or_update_telegram_user(
        self, 
        telegram_id: int,
        username: str | None = None,
        phone_number: str | None = None,
        language_code: str | None = None
    ) -> User:
        """Register a new Telegram user or update existing one"""
        existing_user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if existing_user:
            # Update existing user with new information
            if username is not None:
                existing_user.username = username
            if phone_number is not None:
                existing_user.phone_number = phone_number
            if language_code is not None:
                existing_user.language_code = language_code
            
            return await self.user_repository.update(existing_user)
        else:
            # Create new user
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                phone_number=phone_number,
                language_code=language_code or "ru",
                is_active=True
            )
            
            return await self.user_repository.create(new_user)