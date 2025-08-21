"""
Сервис бронирования
"""

from typing import List, Optional
from uuid import UUID

from domain.booking.entities import Booking, BookingRequest
from domain.booking.ports import AvailabilityService, BookingRepository, NotificationService


class BookingService:
    def __init__(
        self,
        # booking_repository: BookingRepository,
        # availability_service: AvailabilityService,
        # notification_service: NotificationService,
    ):
        # self.booking_repository = booking_repository
        # self.availability_service = availability_service
        # self.notification_service = notification_service
        pass
    
    async def create_booking(self, request: BookingRequest) -> Booking:
        """Создать новое бронирование"""
        
        # Проверяем доступность слота
        is_available = await self.availability_service.is_slot_available(
            request.start_date.strftime("%Y-%m-%d"),
            request.start_time,
            request.finish_date.strftime("%Y-%m-%d"),
            request.finish_time,
        )
        
        if not is_available:
            raise ValueError("Выбранный слот недоступен")
        
        # Создаем бронирование
        booking = Booking(
            user_id=request.user_id,
            tariff=request.tariff,
            start_date=request.start_date,
            start_time=request.start_time,
            finish_date=request.finish_date,
            finish_time=request.finish_time,
            first_bedroom=request.first_bedroom,
            second_bedroom=request.second_bedroom,
            sauna=request.sauna,
            photoshoot=request.photoshoot,
            secret_room=request.secret_room,
            number_guests=request.number_guests,
            contact=request.contact,
            comment=request.comment,
        )
        
        # Сохраняем в репозитории
        saved_booking = await self.booking_repository.create(booking)
        
        # Отправляем уведомление
        await self.notification_service.send_booking_confirmation(saved_booking)
        
        return saved_booking
    
    async def get_booking(self, booking_id: UUID) -> Optional[Booking]:
        """Получить бронирование по ID"""
        return await self.booking_repository.get_by_id(booking_id)
    
    async def get_user_bookings(self, user_id: int) -> List[Booking]:
        """Получить все бронирования пользователя"""
        return await self.booking_repository.get_by_user_id(user_id)
    
    async def cancel_booking(self, booking_id: UUID) -> bool:
        """Отменить бронирование"""
        booking = await self.booking_repository.get_by_id(booking_id)
        if not booking:
            return False
        
        booking.status = "cancelled"
        await self.booking_repository.update(booking)
        await self.notification_service.send_booking_cancellation(booking)
        
        return True
    
    async def check_availability(self, start_date: str, end_date: str) -> List[str]:
        """Проверить доступность на указанные даты"""
        return await self.availability_service.check_availability(start_date, end_date)
