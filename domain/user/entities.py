"""
User domain entities

Domain models for user management and Telegram user integration.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    """User domain entity for Telegram bot users"""
    
    id: UUID = Field(default_factory=uuid4, description="Internal user ID")
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram @username")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    language_code: str = Field(default="ru", description="User's language preference")
    is_active: bool = Field(default=True, description="Whether user account is active")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile with additional preferences"""
    
    user_id: UUID = Field(..., description="Reference to User ID")
    telegram_id: int = Field(..., description="Telegram user ID for quick lookup")
    notification_preferences: dict = Field(default_factory=dict, description="User notification settings")
    booking_preferences: dict = Field(default_factory=dict, description="Default booking preferences")
    interaction_count: int = Field(default=0, description="Number of bot interactions")
    last_interaction_at: Optional[datetime] = Field(None, description="Last bot interaction timestamp")
    
    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """Request to create a new user from Telegram interaction"""
    
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram @username")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    language_code: str = Field(default="ru", description="User's language preference")


class UserUpdateRequest(BaseModel):
    """Request to update user information"""
    
    username: Optional[str] = Field(None, description="Updated @username")
    phone_number: Optional[str] = Field(None, description="Updated phone number")
    language_code: Optional[str] = Field(None, description="Updated language preference")
    is_active: Optional[bool] = Field(None, description="Updated active status")