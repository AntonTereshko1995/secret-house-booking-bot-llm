"""
Интеграционные тесты для полного потока проверки доступности
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from zoneinfo import ZoneInfo

from infrastructure.llm.graphs.available_dates.availability_node import (
    availability_node,
)
from infrastructure.llm.extractors.date_extractor import DateExtractor
from application.services.availability_service import AvailabilityService
from domain.booking.availability import AvailabilitySlot, AvailabilityPeriod

# Timezone для тестов
TZ = ZoneInfo("Europe/Minsk")


class TestAvailableDatesFlow:
    """
    Интеграционные тесты для полного потока проверки доступности.
    Тестирует взаимодействие между DateExtractor, AvailabilityService и availability_node.
    """

    @pytest.fixture
    def fixed_now(self):
        """Фиксированное время для предсказуемых тестов"""
        return datetime(2025, 3, 15, 12, 0, 0, tzinfo=TZ)

    @pytest.mark.asyncio
    async def test_full_flow_month_query_russian(self, fixed_now):
        """Тест полного потока для запроса месяца на русском языке"""
        user_query = {"text": "какие даты свободны в марте?"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата сервиса
                    start_date = fixed_now.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = start_date.replace(day=31, hour=23, minute=59, second=59)

                    # Создаем слоты - все доступны
                    slots = []
                    current_date = start_date.date()
                    while current_date <= end_date.date():
                        slots.append(
                            AvailabilitySlot(
                                date=datetime.combine(
                                    current_date, datetime.min.time(), TZ
                                ),
                                is_available=True,
                            )
                        )
                        current_date += timedelta(days=1)

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=31,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат
                    assert "reply" in result
                    assert (
                        "Отлично! Все 31 дней в март свободны для бронирования"
                        in result["reply"]
                    )
                    assert "Хотите забронировать?" in result["reply"]
                    assert result["availability_data"].total_available_days == 31

                    # Проверяем извлеченные даты
                    dates_extracted = result["dates_extracted"]
                    assert dates_extracted["matched_text"] == "март"

                    # Проверяем вызов сервиса
                    mock_service.get_availability_for_period.assert_called_once()
                    call_args = mock_service.get_availability_for_period.call_args[0]
                    assert call_args[0].month == 3  # start_date
                    assert call_args[1].month == 3  # end_date

    @pytest.mark.asyncio
    async def test_full_flow_specific_date_russian(self, fixed_now):
        """Тест полного потока для конкретной даты на русском языке"""
        user_query = {"text": "свободно ли 25 марта?"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата для одного дня
                    target_date = datetime(2025, 3, 25, tzinfo=TZ)
                    start_date = target_date.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = target_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )

                    slots = [AvailabilitySlot(date=start_date, is_available=True)]

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=1,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат
                    assert "reply" in result
                    assert (
                        "Отлично! Все 1 дней в 25 марта свободны для бронирования"
                        in result["reply"]
                    )
                    assert result["availability_data"].total_available_days == 1

                    # Проверяем извлеченные даты
                    dates_extracted = result["dates_extracted"]
                    assert dates_extracted["matched_text"] == "25 марта"

    @pytest.mark.asyncio
    async def test_full_flow_date_range_russian(self, fixed_now):
        """Тест полного потока для диапазона дат на русском языке"""
        user_query = {"text": "есть ли свободные дни с 20 по 25 марта?"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата для диапазона
                    start_date = datetime(2025, 3, 20, tzinfo=TZ)
                    end_date = datetime(2025, 3, 25, 23, 59, 59, tzinfo=TZ)

                    # Создаем слоты - первые 3 дня свободны, остальные заняты
                    slots = []
                    for i in range(6):  # 20-25 марта = 6 дней
                        slot_date = start_date + timedelta(days=i)
                        slots.append(
                            AvailabilitySlot(
                                date=slot_date,
                                is_available=i < 3,  # Первые 3 дня свободны
                            )
                        )

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=3,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат
                    assert "reply" in result
                    assert "В 20-25 марта свободно 3 из 6 дней" in result["reply"]
                    assert "Свободные даты:" in result["reply"]
                    assert "20.03, 21.03, 22.03" in result["reply"]
                    assert result["availability_data"].total_available_days == 3

    @pytest.mark.asyncio
    async def test_full_flow_no_available_dates(self, fixed_now):
        """Тест полного потока когда нет доступных дат"""
        user_query = {"text": "что свободно в марте?"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата - нет свободных дней
                    start_date = fixed_now.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = start_date.replace(day=31, hour=23, minute=59, second=59)

                    # Все слоты заняты
                    slots = []
                    current_date = start_date.date()
                    while current_date <= end_date.date():
                        slots.append(
                            AvailabilitySlot(
                                date=datetime.combine(
                                    current_date, datetime.min.time(), TZ
                                ),
                                is_available=False,
                            )
                        )
                        current_date += timedelta(days=1)

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=0,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат
                    assert "reply" in result
                    assert "К сожалению, на март нет свободных дней" in result["reply"]
                    assert "Попробуйте выбрать другие даты" in result["reply"]
                    assert result["availability_data"].total_available_days == 0

    @pytest.mark.asyncio
    async def test_full_flow_english_query(self, fixed_now):
        """Тест полного потока для запроса на английском языке"""
        user_query = {"text": "available dates in March?"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата
                    start_date = fixed_now.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = start_date.replace(day=31, hour=23, minute=59, second=59)

                    slots = []
                    for i in range(31):
                        slot_date = start_date + timedelta(days=i)
                        slots.append(
                            AvailabilitySlot(
                                date=slot_date,
                                is_available=i < 15,  # Первая половина месяца свободна
                            )
                        )

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=15,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат
                    assert "reply" in result
                    assert "В march свободно 15 из 31 дней" in result["reply"]
                    assert result["availability_data"].total_available_days == 15

                    # Проверяем извлеченные даты
                    dates_extracted = result["dates_extracted"]
                    assert dates_extracted["matched_text"] == "march"

    @pytest.mark.asyncio
    async def test_full_flow_numeric_date_query(self, fixed_now):
        """Тест полного потока для запроса с цифровой датой"""
        user_query = {"text": "свободно ли 25.03?"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата для одного дня (занят)
                    target_date = datetime(2025, 3, 25, tzinfo=TZ)
                    start_date = target_date.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = target_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )

                    slots = [
                        AvailabilitySlot(
                            date=start_date, is_available=False  # Дата занята
                        )
                    ]

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=0,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат
                    assert "reply" in result
                    assert "К сожалению, на 25.03 нет свободных дней" in result["reply"]
                    assert result["availability_data"].total_available_days == 0

                    # Проверяем извлеченные даты
                    dates_extracted = result["dates_extracted"]
                    assert dates_extracted["matched_text"] == "25.03"

    @pytest.mark.asyncio
    async def test_full_flow_service_error_handling(self, fixed_now):
        """Тест обработки ошибок сервиса"""
        user_query = {"text": "март доступность"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Настраиваем сервис для генерации ошибки
                    mock_service.get_availability_for_period = AsyncMock(
                        side_effect=Exception("Database connection error")
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем обработку ошибки
                    assert "reply" in result
                    assert (
                        "Произошла ошибка при проверке доступности" in result["reply"]
                    )
                    assert "error" in result
                    assert result["error"] == "Database connection error"

    @pytest.mark.asyncio
    async def test_full_flow_current_month_fallback(self, fixed_now):
        """Тест fallback на текущий месяц для неопределенного запроса"""
        user_query = {"text": "проверить доступность"}

        with patch(
            "infrastructure.llm.extractors.date_extractor.datetime"
        ) as mock_datetime:
            with patch("infrastructure.llm.extractors.date_extractor.get_llm"):
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем мок времени
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.combine = datetime.combine
                    mock_datetime.side_effect = lambda *args, **kw: datetime(
                        *args, **kw
                    )

                    # Создаем мок результата для текущего месяца
                    start_date = fixed_now.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = start_date.replace(day=31, hour=23, minute=59, second=59)

                    slots = []
                    for i in range(31):
                        slots.append(
                            AvailabilitySlot(
                                date=start_date + timedelta(days=i), is_available=True
                            )
                        )

                    mock_availability_period = AvailabilityPeriod(
                        start_date=start_date,
                        end_date=end_date,
                        slots=slots,
                        total_available_days=31,
                    )

                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_availability_period
                    )

                    # Выполняем полный поток
                    result = await availability_node(user_query)

                    # Проверяем результат - должен использовать current month как fallback
                    assert "reply" in result
                    assert "availability_data" in result

                    # Проверяем извлеченные даты - должно быть "current month"
                    dates_extracted = result["dates_extracted"]
                    assert dates_extracted["matched_text"] == "current month"
