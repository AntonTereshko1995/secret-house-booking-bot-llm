"""
Application Layer

Contains application services and orchestration logic.
"""

from .services import (
    BookingService, 
    UserService, 
    ChatService,
    AvailabilityService,
    FAQService,
    PricingService
)

async def initialize_application():
    """Initialize the application with all dependencies"""
    from infrastructure.container import init_container
    await init_container()

async def shutdown_application():
    """Shutdown the application and cleanup resources"""
    from infrastructure.container import close_container
    await close_container()

__all__ = [
    "BookingService",
    "UserService", 
    "ChatService",
    "AvailabilityService",
    "FAQService",
    "PricingService",
    "initialize_application",
    "shutdown_application",
]
