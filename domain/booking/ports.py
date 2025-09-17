"""
Порты (интерфейсы) для доменной логики
"""

from abc import ABC, abstractmethod
from uuid import UUID

from .entities import Booking


class BookingRepository(ABC):
    """Port for booking repository"""

    @abstractmethod
    async def create(self, booking: Booking) -> Booking:
        """Create a new booking"""
        pass

    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        """Get booking by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[Booking]:
        """Get all bookings for a user"""
        pass

    @abstractmethod
    async def update(self, booking: Booking) -> Booking:
        """Update booking"""
        pass

    @abstractmethod
    async def delete(self, booking_id: UUID) -> bool:
        """Delete booking"""
        pass

    @abstractmethod
    async def get_all(self) -> list[Booking]:
        """Get all bookings"""
        pass

    @abstractmethod
    async def find_by_date_range(
        self, start_date: str, end_date: str
    ) -> list[Booking]:
        """Find bookings within a date range"""
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> list[Booking]:
        """Find bookings by status"""
        pass

    @abstractmethod
    async def modify_booking_level(
        self, booking_id: UUID, new_level: str, modification_reason: str
    ) -> Booking:
        """Modify booking level with audit trail"""
        pass

    @abstractmethod
    async def get_booking_modifications(self, booking_id: UUID) -> list[dict]:
        """Get all modifications for a booking"""
        pass


class AvailabilityService(ABC):
    """Port for availability service"""

    @abstractmethod
    async def check_availability(self, start_date: str, end_date: str) -> list[str]:
        """Check availability for specified dates"""
        pass

    @abstractmethod
    async def is_slot_available(
        self, start_date: str, start_time: str, end_date: str, end_time: str
    ) -> bool:
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
