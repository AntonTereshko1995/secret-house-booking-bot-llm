"""
User domain ports (interfaces)
"""

from abc import ABC, abstractmethod
from uuid import UUID

from .entities import User


class UserRepository(ABC):
    """Port for user repository"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        """Get all users"""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """Find user by username"""
        pass