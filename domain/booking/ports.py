"""
Порты (интерфейсы) для доменной логики
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import Booking, BookingRequest


class BookingRepository(ABC):
    """Port for booking repository"""
    
    @abstractmethod
    async def create(self, booking: Booking) -> Booking:
        """Create booking"""
        pass
    
    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """Get booking by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[Booking]:
        """Get user bookings"""
        pass
    
    @abstractmethod
    async def update(self, booking: Booking) -> Booking:
        """Update booking"""
        pass
    
    @abstractmethod
    async def delete(self, booking_id: UUID) -> bool:
        """Delete booking"""
        pass


class AvailabilityService(ABC):
    """Port for availability service"""
    
    @abstractmethod
    async def check_availability(self, start_date: str, end_date: str) -> List[str]:
        """Check availability for specified dates"""
        pass
    
    @abstractmethod
    async def is_slot_available(self, start_date: str, start_time: str, end_date: str, end_time: str) -> bool:
        """Check availability of specific slot"""
        pass


class NotificationService(ABC):
    """Port for notification service"""
    
    @abstractmethod
    async def send_booking_confirmation(self, booking: Booking) -> None:
        """Send booking confirmation"""
        pass
    
    @abstractmethod
    async def send_booking_cancellation(self, booking: Booking) -> None:
        """Send booking cancellation notification"""
        pass
