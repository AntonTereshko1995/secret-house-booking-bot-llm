"""
Сервис проверки доступности
"""

from datetime import datetime, timedelta
from typing import List
from zoneinfo import ZoneInfo

from core.config import settings
from core.logging import get_logger
from domain.booking.availability import AvailabilitySlot, AvailabilityPeriod
from domain.booking.entities import Booking

logger = get_logger(__name__)
TZ = ZoneInfo(settings.timezone)


class AvailabilityService:
    """Сервис для проверки доступности дат"""

    def __init__(self):
        # В будущем здесь будут зависимости:
        # - booking_repository: BookingRepository
        # - config: AvailabilityConfig
        pass

    async def get_availability_for_period(
        self, start_date: datetime, end_date: datetime
    ) -> AvailabilityPeriod:
        """
        Получить информацию о доступности для указанного периода

        Args:
            start_date: Начальная дата периода
            end_date: Конечная дата периода

        Returns:
            AvailabilityPeriod: Период с информацией о доступности

        Raises:
            ValueError: Если даты некорректны
        """
        logger.info(
            "Checking availability",
            extra={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

        # Валидация дат
        validated_start = self._ensure_timezone_aware(start_date)
        validated_end = self._ensure_timezone_aware(end_date)

        if validated_start > validated_end:
            raise ValueError("Начальная дата не может быть больше конечной")

        if validated_start.date() < datetime.now(TZ).date():
            logger.warning("Запрос доступности для прошедших дат")

        # Получение существующих бронирований (временно мокаем)
        existing_bookings = await self._get_bookings_for_period(
            validated_start, validated_end
        )

        # Генерация слотов доступности по дням
        slots = []
        current_date = validated_start.date()

        while current_date <= validated_end.date():
            # Проверка, есть ли бронирование на эту дату
            is_booked = self._is_date_booked(current_date, existing_bookings)

            slot_datetime = datetime.combine(current_date, datetime.min.time(), TZ)
            slot = AvailabilitySlot(
                date=slot_datetime,
                is_available=not is_booked,
                booking_id=(
                    self._get_booking_id_for_date(current_date, existing_bookings)
                    if is_booked
                    else None
                ),
            )
            slots.append(slot)

            current_date += timedelta(days=1)

        total_available = sum(1 for slot in slots if slot.is_available)

        return AvailabilityPeriod(
            start_date=validated_start,
            end_date=validated_end,
            slots=slots,
            total_available_days=total_available,
        )

    def _ensure_timezone_aware(self, dt: datetime) -> datetime:
        """Убедиться, что datetime объект имеет информацию о часовом поясе"""
        if dt.tzinfo is None:
            # Если timezone не указан, используем настройки проекта
            return dt.replace(tzinfo=TZ)
        return dt

    async def _get_bookings_for_period(
        self, start_date: datetime, end_date: datetime
    ) -> List[Booking]:
        """
        Получить существующие бронирования для периода

        ВРЕМЕННАЯ ЗАГЛУШКА: В будущем это будет запрос к репозиторию
        """
        # TODO: Реализовать запрос к BookingRepository
        # return await self.booking_repository.get_bookings_by_date_range(start_date, end_date)

        # Временно возвращаем пустой список
        logger.debug("Using mock booking data - no real bookings returned")
        return []

    def _is_date_booked(self, date, bookings: List[Booking]) -> bool:
        """Проверить, забронирована ли конкретная дата"""
        for booking in bookings:
            if booking.start_date.date() <= date <= booking.finish_date.date():
                return True
        return False

    def _get_booking_id_for_date(self, date, bookings: List[Booking]):
        """Получить ID бронирования для конкретной даты"""
        for booking in bookings:
            if booking.start_date.date() <= date <= booking.finish_date.date():
                return booking.id
        return None
