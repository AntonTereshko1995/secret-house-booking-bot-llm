"""
Порты (интерфейсы) для доменной логики
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import Booking, BookingRequest


class BookingRepository(ABC):
    """Порт для репозитория бронирований"""
    
    @abstractmethod
    async def create(self, booking: Booking) -> Booking:
        """Создать бронирование"""
        pass
    
    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """Получить бронирование по ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[Booking]:
        """Получить бронирования пользователя"""
        pass
    
    @abstractmethod
    async def update(self, booking: Booking) -> Booking:
        """Обновить бронирование"""
        pass
    
    @abstractmethod
    async def delete(self, booking_id: UUID) -> bool:
        """Удалить бронирование"""
        pass


class AvailabilityService(ABC):
    """Порт для сервиса проверки доступности"""
    
    @abstractmethod
    async def check_availability(self, start_date: str, end_date: str) -> List[str]:
        """Проверить доступность на указанные даты"""
        pass
    
    @abstractmethod
    async def is_slot_available(self, start_date: str, start_time: str, end_date: str, end_time: str) -> bool:
        """Проверить доступность конкретного слота"""
        pass


class NotificationService(ABC):
    """Порт для сервиса уведомлений"""
    
    @abstractmethod
    async def send_booking_confirmation(self, booking: Booking) -> None:
        """Отправить подтверждение бронирования"""
        pass
    
    @abstractmethod
    async def send_booking_cancellation(self, booking: Booking) -> None:
        """Отправить уведомление об отмене бронирования"""
        pass
