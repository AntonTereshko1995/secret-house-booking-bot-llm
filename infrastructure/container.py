from dependency_injector import containers, providers
from core.config import settings
from infrastructure.db.connection import DatabaseConnection
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.booking_repository import BookingRepository
from infrastructure.db.repositories.chat_repository import ChatRepository
from application.services.user_service import UserService
from application.services.booking_service import BookingService
from application.services.chat_service import ChatService
from application.services.availability_service import AvailabilityService

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Database
    database = providers.Singleton(
        DatabaseConnection,
        database_url=settings.database_url
    )
    
    # Services
    availability_service = providers.Singleton(
        AvailabilityService
    )


# Global container instance
container = Container()

# Convenience functions for backward compatibility
async def get_user_service() -> UserService:
    """Get user service instance"""
    session = await container.database().get_session()
    user_repository = UserRepository(session)
    return UserService(user_repository)

async def get_chat_service() -> ChatService:
    """Get chat service instance"""
    session = await container.database().get_session()
    chat_repository = ChatRepository(session)
    return ChatService(chat_repository)

async def get_booking_service() -> BookingService:
    """Get booking service instance"""
    session = await container.database().get_session()
    booking_repository = BookingRepository(session)
    availability_service = container.availability_service()
    return BookingService(
        booking_repository=booking_repository,
        availability_service=availability_service,
        notification_service=None  # TODO: Add when implemented
    )

def get_availability_service() -> AvailabilityService:
    """Get availability service instance"""
    return container.availability_service()

async def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    session = await container.database().get_session()
    return UserRepository(session)

async def get_booking_repository() -> BookingRepository:
    """Get booking repository instance"""
    session = await container.database().get_session()
    return BookingRepository(session)

async def get_chat_repository() -> ChatRepository:
    """Get chat repository instance"""
    session = await container.database().get_session()
    return ChatRepository(session)

# Initialize container
async def init_container():
    """Initialize the container and resources"""
    await container.database().connect()

async def close_container():
    """Close container and cleanup resources"""
    await container.database().close()