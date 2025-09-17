from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

from application.services.availability_service import (
    AvailabilityService as AvailabilityServiceImpl,
)
from domain.booking.availability import AvailabilityPeriod
from domain.booking.entities import Booking, BookingRequest

if TYPE_CHECKING:
    from domain.booking.ports import BookingRepository, AvailabilityService, NotificationService


class BookingService:
    def __init__(
        self,
        booking_repository: "BookingRepository",
        availability_service: "AvailabilityService", 
        notification_service: "NotificationService",
    ):
        self.booking_repository = booking_repository
        self.availability_service = availability_service
        self.notification_service = notification_service

    async def create_booking(self, request: BookingRequest) -> Booking:
        """Create new booking"""

        # Check slot availability
        is_available = await self.availability_service.is_slot_available(
            request.start_date.strftime("%Y-%m-%d"),
            request.start_date,
            request.finish_date.strftime("%Y-%m-%d"),
            request.finish_date,
        )

        if not is_available:
            raise ValueError("Выбранный слот недоступен")

        # Create booking
        booking = Booking(
            user_id=request.user_id,
            tariff=request.tariff,
            start_date=request.start_date,
            finish_date=request.finish_date,
            green_bedroom=request.green_bedroom,
            white_bedroom=request.white_bedroom,
            sauna=request.sauna,
            photoshoot=request.photoshoot,
            secret_room=request.secret_room,
            number_guests=request.number_guests,
            comment=request.comment,
            price=request.price
        )

        # Save in repository
        saved_booking = await self.booking_repository.create(booking)

        # Send notification
        await self.notification_service.send_booking_confirmation(saved_booking)

        return saved_booking

    async def get_booking(self, booking_id: UUID) -> Booking | None:
        """Get booking by ID"""
        return await self.booking_repository.get_by_id(booking_id)

    async def get_user_bookings(self, user_id: UUID) -> list[Booking]:
        """Get all user bookings"""
        return await self.booking_repository.get_by_user_id(user_id)

    async def cancel_booking(self, booking_id: UUID) -> bool:
        """Cancel booking"""
        booking = await self.booking_repository.get_by_id(booking_id)
        if not booking:
            return False

        booking.status = "cancelled"
        await self.booking_repository.update(booking)
        await self.notification_service.send_booking_cancellation(booking)

        return True

    async def modify_booking_level(
        self, booking_id: UUID, new_level: str, modification_reason: str
    ) -> Booking:
        """Modify booking level with audit trail"""
        return await self.booking_repository.modify_booking_level(
            booking_id, new_level, modification_reason
        )

    async def get_booking_modifications(self, booking_id: UUID) -> list[dict]:
        """Get all modifications for a booking"""
        return await self.booking_repository.get_booking_modifications(booking_id)

    async def find_bookings_by_date_range(
        self, start_date: str, end_date: str
    ) -> list[Booking]:
        """Find bookings within a date range"""
        return await self.booking_repository.find_by_date_range(start_date, end_date)

    async def find_bookings_by_status(self, status: str) -> list[Booking]:
        """Find bookings by status"""
        return await self.booking_repository.find_by_status(status)

    async def check_availability(self, start_date: str, end_date: str) -> list[str]:
        """Check availability for specified dates"""
        return await self.availability_service.check_availability(start_date, end_date)

    async def availability_for_period(
        self, start_date: datetime, end_date: datetime
    ) -> AvailabilityPeriod:
        """
        Получить подробную информацию о доступности для периода

        Args:
            start_date: Начальная дата периода
            end_date: Конечная дата периода

        Returns:
            AvailabilityPeriod: Подробная информация о доступности
        """
        availability_service = AvailabilityServiceImpl()
        return await availability_service.get_availability_for_period(
            start_date, end_date
        )
