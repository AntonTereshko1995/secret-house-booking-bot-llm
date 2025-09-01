"""
Тесты для AvailabilityService
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from zoneinfo import ZoneInfo

from application.services.availability_service import AvailabilityService
from domain.booking.availability import AvailabilitySlot, AvailabilityPeriod
from domain.booking.entities import Booking

# Timezone для тестов
TZ = ZoneInfo("Europe/Minsk")


class TestAvailabilityService:

    @pytest.fixture
    def availability_service(self):
        """Создает экземпляр AvailabilityService для тестов"""
        return AvailabilityService()

    @pytest.fixture
    def sample_dates(self):
        """Создает примерные даты для тестов"""
        now = datetime.now(TZ)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=30)
        return start_date, end_date

    @pytest.fixture
    def mock_booking(self):
        """Создает мок-бронирование для тестов"""
        now = datetime.now(TZ)
        return Booking(
            user_id=123,
            tariff="standard",
            start_date=now + timedelta(days=5),
            start_time="14:00",
            finish_date=now + timedelta(days=7),
            finish_time="12:00",
            first_bedroom=True,
            second_bedroom=False,
            sauna=False,
            photoshoot=False,
            secret_room=False,
            number_guests=2,
            contact="test@example.com",
            status="confirmed",
        )

    @pytest.mark.asyncio
    async def test_get_availability_for_period_all_available(
        self, availability_service, sample_dates
    ):
        """Тест когда все даты в периоде доступны"""
        start_date, end_date = sample_dates

        # Мокаем метод получения бронирований (возвращаем пустой список)
        with patch.object(
            availability_service, "_get_bookings_for_period", new_callable=AsyncMock
        ) as mock_get_bookings:
            mock_get_bookings.return_value = []

            result = await availability_service.get_availability_for_period(
                start_date, end_date
            )

            # Проверяем результат
            assert isinstance(result, AvailabilityPeriod)
            assert result.start_date == start_date
            assert result.end_date == end_date
            assert result.total_available_days == 31  # Март имеет 31 день
            assert all(slot.is_available for slot in result.slots)
            assert len(result.slots) == 31

    @pytest.mark.asyncio
    async def test_get_availability_for_period_with_bookings(
        self, availability_service, sample_dates, mock_booking
    ):
        """Тест доступности с существующими бронированиями"""
        start_date, end_date = sample_dates

        # Мокаем метод получения бронирований
        with patch.object(
            availability_service, "_get_bookings_for_period", new_callable=AsyncMock
        ) as mock_get_bookings:
            mock_get_bookings.return_value = [mock_booking]

            result = await availability_service.get_availability_for_period(
                start_date, end_date
            )

            # Проверяем результат
            assert isinstance(result, AvailabilityPeriod)
            assert result.total_available_days < 31  # Некоторые дни заняты

            # Проверяем, что заблокированные дни действительно заблокированы
            booked_slots = [slot for slot in result.slots if not slot.is_available]
            assert len(booked_slots) == 3  # 3 дня бронирования (5-7 число)

            for slot in booked_slots:
                assert slot.booking_id == mock_booking.id

    @pytest.mark.asyncio
    async def test_get_availability_invalid_date_range(self, availability_service):
        """Тест с некорректным диапазоном дат (начальная дата больше конечной)"""
        start_date = datetime(2025, 3, 31, tzinfo=TZ)
        end_date = datetime(2025, 3, 1, tzinfo=TZ)

        with pytest.raises(
            ValueError, match="Начальная дата не может быть больше конечной"
        ):
            await availability_service.get_availability_for_period(start_date, end_date)

    @pytest.mark.asyncio
    async def test_get_availability_single_day(self, availability_service):
        """Тест для одного дня"""
        target_date = datetime(2025, 3, 15, tzinfo=TZ)

        with patch.object(
            availability_service, "_get_bookings_for_period", new_callable=AsyncMock
        ) as mock_get_bookings:
            mock_get_bookings.return_value = []

            result = await availability_service.get_availability_for_period(
                target_date, target_date
            )

            assert len(result.slots) == 1
            assert result.total_available_days == 1
            assert result.slots[0].is_available
            assert result.slots[0].date.date() == target_date.date()

    def test_ensure_timezone_aware(self, availability_service):
        """Тест корректной обработки часовых поясов"""
        # Naive datetime (без timezone)
        naive_dt = datetime(2025, 3, 15, 12, 0, 0)
        result = availability_service._ensure_timezone_aware(naive_dt)

        assert result.tzinfo is not None
        assert result.tzinfo == TZ

        # Timezone-aware datetime (с timezone)
        aware_dt = datetime(2025, 3, 15, 12, 0, 0, tzinfo=TZ)
        result = availability_service._ensure_timezone_aware(aware_dt)

        assert result == aware_dt
        assert result.tzinfo == TZ

    def test_is_date_booked(self, availability_service, mock_booking):
        """Тест проверки, забронирована ли дата"""
        bookings = [mock_booking]

        # Дата внутри бронирования
        booked_date = mock_booking.start_date.date() + timedelta(days=1)
        assert availability_service._is_date_booked(booked_date, bookings)

        # Дата вне бронирования
        free_date = mock_booking.start_date.date() - timedelta(days=1)
        assert not availability_service._is_date_booked(free_date, bookings)

        # Граничные даты
        start_date = mock_booking.start_date.date()
        end_date = mock_booking.finish_date.date()
        assert availability_service._is_date_booked(start_date, bookings)
        assert availability_service._is_date_booked(end_date, bookings)

    def test_get_booking_id_for_date(self, availability_service, mock_booking):
        """Тест получения ID бронирования для даты"""
        bookings = [mock_booking]

        # Дата внутри бронирования
        booked_date = mock_booking.start_date.date() + timedelta(days=1)
        booking_id = availability_service._get_booking_id_for_date(
            booked_date, bookings
        )
        assert booking_id == mock_booking.id

        # Дата вне бронирования
        free_date = mock_booking.start_date.date() - timedelta(days=1)
        booking_id = availability_service._get_booking_id_for_date(free_date, bookings)
        assert booking_id is None

    @pytest.mark.asyncio
    async def test_get_availability_past_dates_warning(self, availability_service):
        """Тест предупреждения для прошедших дат"""
        # Прошедшая дата
        past_date = datetime.now(TZ) - timedelta(days=5)
        end_date = past_date + timedelta(days=3)

        with patch.object(
            availability_service, "_get_bookings_for_period", new_callable=AsyncMock
        ) as mock_get_bookings:
            mock_get_bookings.return_value = []

            # Проверяем, что предупреждение записывается в лог
            with patch(
                "application.services.availability_service.logger"
            ) as mock_logger:
                result = await availability_service.get_availability_for_period(
                    past_date, end_date
                )

                mock_logger.warning.assert_called_once_with(
                    "Запрос доступности для прошедших дат"
                )
                assert isinstance(result, AvailabilityPeriod)

    @pytest.mark.asyncio
    async def test_get_availability_timezone_conversion(self, availability_service):
        """Тест корректности работы с разными часовыми поясами"""
        # Создаем даты в UTC
        utc_tz = ZoneInfo("UTC")
        start_utc = datetime(2025, 3, 15, 10, 0, 0, tzinfo=utc_tz)
        end_utc = datetime(2025, 3, 15, 22, 0, 0, tzinfo=utc_tz)

        with patch.object(
            availability_service, "_get_bookings_for_period", new_callable=AsyncMock
        ) as mock_get_bookings:
            mock_get_bookings.return_value = []

            result = await availability_service.get_availability_for_period(
                start_utc, end_utc
            )

            # Результат должен быть в таймзоне проекта (Europe/Minsk)
            assert result.start_date.tzinfo == TZ or result.start_date.tzinfo == utc_tz
            assert len(result.slots) == 1  # Один день
            assert result.total_available_days == 1
