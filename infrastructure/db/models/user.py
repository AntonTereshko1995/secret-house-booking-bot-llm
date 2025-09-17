"""
User database model

SQLAlchemy model for Telegram bot users with profile information.
"""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserModel(BaseModel):
    """User model for Telegram bot users"""
    __tablename__ = "users"
    
    # Telegram user identification
    telegram_id = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="Telegram user ID"
    )
    
    # User profile information
    username = Column(
        String(255),
        nullable=True,
        comment="Telegram @username (without @)"
    )
    
    phone_number = Column(
        String(20),
        nullable=True,
        comment="User's phone number"
    )
    
    # User preferences
    language_code = Column(
        String(10),
        nullable=False,
        default="ru",
        comment="User's preferred language (ISO code)"
    )
    
    # Account status
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the user account is active"
    )
    
    # Relationships
    bookings = relationship(
        "BookingModel",
        back_populates="user",
        lazy="select",
        cascade="all, delete-orphan"
    )
    
    chat_sessions = relationship(
        "ChatSessionModel",
        back_populates="user",
        lazy="select",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation"""
        return f"<UserModel(telegram_id={self.telegram_id}, username={self.username})>"