"""
Database models module

Contains all SQLAlchemy database models for the Secret House booking bot.
"""

from .base import Base, BaseModel
from .booking import BookingModel
from .chat import ChatSessionModel
from .user import UserModel

# Ensure all models are imported for Alembic autodiscovery
__all__ = [
    "Base",
    "BaseModel", 
    "BookingModel",
    "ChatSessionModel",
    "UserModel"
]

# Import all models to ensure they're registered with Base.metadata
# This is required for Alembic to detect the models
_models = [BookingModel, ChatSessionModel, UserModel]