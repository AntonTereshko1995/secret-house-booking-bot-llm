"""
Тесты для availability_node
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from zoneinfo import ZoneInfo

from infrastructure.llm.graphs.available_dates.availability_node import (
    availability_node,
    _format_availability_response,
)
from domain.booking.availability import AvailabilitySlot, AvailabilityPeriod

# Timezone для тестов
TZ = ZoneInfo("Europe/Minsk")


class TestAvailabilityNode:

    @pytest.fixture
    def mock_app_state(self):
        """Создает мок состояния приложения"""
        return {"text": "какие даты свободны в марте?"}

    @pytest.fixture
    def mock_availability_period_all_free(self):
        """Создает мок AvailabilityPeriod где все дни свободны"""
        now = datetime.now(TZ)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=30)

        slots = []
        for i in range(31):  # Март - 31 день
            slot_date = start_date + timedelta(days=i)
            slots.append(AvailabilitySlot(date=slot_date, is_available=True))

        return AvailabilityPeriod(
            start_date=start_date,
            end_date=end_date,
            slots=slots,
            total_available_days=31,
        )

    @pytest.fixture
    def mock_availability_period_partial(self):
        """Создает мок AvailabilityPeriod где только часть дней свободна"""
        now = datetime.now(TZ)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=30)

        slots = []
        for i in range(31):
            slot_date = start_date + timedelta(days=i)
            # Каждый третий день занят
            is_available = (i + 1) % 3 != 0
            slots.append(AvailabilitySlot(date=slot_date, is_available=is_available))

        available_count = sum(1 for slot in slots if slot.is_available)

        return AvailabilityPeriod(
            start_date=start_date,
            end_date=end_date,
            slots=slots,
            total_available_days=available_count,
        )

    @pytest.fixture
    def mock_availability_period_no_free(self):
        """Создает мок AvailabilityPeriod где нет свободных дней"""
        now = datetime.now(TZ)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=30)

        slots = []
        for i in range(31):
            slot_date = start_date + timedelta(days=i)
            slots.append(AvailabilitySlot(date=slot_date, is_available=False))

        return AvailabilityPeriod(
            start_date=start_date,
            end_date=end_date,
            slots=slots,
            total_available_days=0,
        )

    @pytest.mark.asyncio
    async def test_availability_node_all_free(
        self, mock_app_state, mock_availability_period_all_free
    ):
        """Тест когда все дни свободны"""
        with patch(
            "infrastructure.llm.graphs.available_dates.availability_node.date_extractor"
        ) as mock_extractor:
            with patch(
                "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
            ) as mock_service:
                # Настраиваем мок извлечения дат
                now = datetime.now(TZ)
                start_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=30)
                mock_extractor.extract_dates_from_text.return_value = (
                    start_date,
                    end_date,
                    "март",
                )

                # Настраиваем мок сервиса
                mock_service.get_availability_for_period = AsyncMock(
                    return_value=mock_availability_period_all_free
                )

                # Вызываем узел
                result = await availability_node(mock_app_state)

                # Проверяем результат
                assert "reply" in result
                assert (
                    "Отлично! Все 31 дней в март свободны для бронирования"
                    in result["reply"]
                )
                assert "Хотите забронировать?" in result["reply"]
                assert "availability_data" in result
                assert "dates_extracted" in result

                # Проверяем, что сервис был вызван с правильными параметрами
                mock_service.get_availability_for_period.assert_called_once_with(
                    start_date, end_date
                )

    @pytest.mark.asyncio
    async def test_availability_node_partial_free(
        self, mock_app_state, mock_availability_period_partial
    ):
        """Тест когда только часть дней свободна"""
        with patch(
            "infrastructure.llm.graphs.available_dates.availability_node.date_extractor"
        ) as mock_extractor:
            with patch(
                "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
            ) as mock_service:
                # Настраиваем моки
                now = datetime.now(TZ)
                start_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=30)
                mock_extractor.extract_dates_from_text.return_value = (
                    start_date,
                    end_date,
                    "март",
                )
                mock_service.get_availability_for_period = AsyncMock(
                    return_value=mock_availability_period_partial
                )

                # Вызываем узел
                result = await availability_node(mock_app_state)

                # Проверяем результат
                assert "reply" in result
                available_count = mock_availability_period_partial.total_available_days
                assert (
                    f"В март свободно {available_count} из 31 дней" in result["reply"]
                )
                assert "Свободные даты:" in result["reply"]
                assert "Хотите забронировать одну из свободных дат?" in result["reply"]

    @pytest.mark.asyncio
    async def test_availability_node_no_free(
        self, mock_app_state, mock_availability_period_no_free
    ):
        """Тест когда нет свободных дней"""
        with patch(
            "infrastructure.llm.graphs.available_dates.availability_node.date_extractor"
        ) as mock_extractor:
            with patch(
                "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
            ) as mock_service:
                # Настраиваем моки
                now = datetime.now(TZ)
                start_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=30)
                mock_extractor.extract_dates_from_text.return_value = (
                    start_date,
                    end_date,
                    "март",
                )
                mock_service.get_availability_for_period = AsyncMock(
                    return_value=mock_availability_period_no_free
                )

                # Вызываем узел
                result = await availability_node(mock_app_state)

                # Проверяем результат
                assert "reply" in result
                assert "К сожалению, на март нет свободных дней" in result["reply"]
                assert "Попробуйте выбрать другие даты" in result["reply"]

    @pytest.mark.asyncio
    async def test_availability_node_error_handling(self, mock_app_state):
        """Тест обработки ошибок"""
        with patch(
            "infrastructure.llm.graphs.available_dates.availability_node.date_extractor"
        ) as mock_extractor:
            with patch(
                "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
            ) as mock_service:
                # Настраиваем мок для генерации ошибки
                mock_extractor.extract_dates_from_text.side_effect = Exception(
                    "Test error"
                )

                # Вызываем узел
                result = await availability_node(mock_app_state)

                # Проверяем, что ошибка обработана корректно
                assert "reply" in result
                assert "Произошла ошибка при проверке доступности" in result["reply"]
                assert "error" in result
                assert result["error"] == "Test error"

    @pytest.mark.asyncio
    async def test_availability_node_empty_text(self):
        """Тест с пустым текстом запроса"""
        app_state = {"text": ""}

        with patch(
            "infrastructure.llm.graphs.available_dates.availability_node.date_extractor"
        ) as mock_extractor:
            with patch(
                "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
            ) as mock_service:
                # date_extractor должен вернуть текущий месяц для пустого запроса
                now = datetime.now(TZ)
                start_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=30)
                mock_extractor.extract_dates_from_text.return_value = (
                    start_date,
                    end_date,
                    "current month",
                )

                # Создаем мок результата
                mock_period = AvailabilityPeriod(
                    start_date=start_date,
                    end_date=end_date,
                    slots=[AvailabilitySlot(date=start_date, is_available=True)],
                    total_available_days=1,
                )
                mock_service.get_availability_for_period = AsyncMock(
                    return_value=mock_period
                )

                # Вызываем узел
                result = await availability_node(app_state)

                # Проверяем, что узел отработал без ошибок
                assert "reply" in result
                assert "availability_data" in result

    @pytest.mark.asyncio
    async def test_availability_node_logging(self, mock_app_state):
        """Тест корректности логирования"""
        with patch(
            "infrastructure.llm.graphs.available_dates.availability_node.logger"
        ) as mock_logger:
            with patch(
                "infrastructure.llm.graphs.available_dates.availability_node.date_extractor"
            ) as mock_extractor:
                with patch(
                    "infrastructure.llm.graphs.available_dates.availability_node.availability_service"
                ) as mock_service:
                    # Настраиваем моки
                    now = datetime.now(TZ)
                    mock_extractor.extract_dates_from_text.return_value = (
                        now,
                        now,
                        "test",
                    )
                    mock_period = AvailabilityPeriod(
                        start_date=now, end_date=now, slots=[], total_available_days=0
                    )
                    mock_service.get_availability_for_period = AsyncMock(
                        return_value=mock_period
                    )

                    # Вызываем узел
                    await availability_node(mock_app_state)

                    # Проверяем логирование
                    mock_logger.info.assert_called_with(
                        "Processing availability request",
                        extra={"user_text": mock_app_state["text"]},
                    )
                    mock_logger.debug.assert_called_once()


class TestFormatAvailabilityResponse:

    @pytest.fixture
    def availability_period_all_free(self):
        """Период где все дни свободны"""
        now = datetime.now(TZ)
        slots = [AvailabilitySlot(date=now, is_available=True) for _ in range(31)]
        return AvailabilityPeriod(
            start_date=now, end_date=now, slots=slots, total_available_days=31
        )

    @pytest.fixture
    def availability_period_partial(self):
        """Период где часть дней свободна (10 из 31)"""
        now = datetime.now(TZ)
        slots = []
        for i in range(31):
            slots.append(
                AvailabilitySlot(
                    date=now + timedelta(days=i),
                    is_available=i < 10,  # Первые 10 дней свободны
                )
            )
        return AvailabilityPeriod(
            start_date=now, end_date=now, slots=slots, total_available_days=10
        )

    @pytest.fixture
    def availability_period_no_free(self):
        """Период без свободных дней"""
        now = datetime.now(TZ)
        slots = [AvailabilitySlot(date=now, is_available=False) for _ in range(31)]
        return AvailabilityPeriod(
            start_date=now, end_date=now, slots=slots, total_available_days=0
        )

    def test_format_all_free(self, availability_period_all_free):
        """Тест форматирования когда все дни свободны"""
        result = _format_availability_response(availability_period_all_free, "март")

        assert "Отлично! Все 31 дней в март свободны для бронирования" in result
        assert "Хотите забронировать?" in result

    def test_format_partial_free(self, availability_period_partial):
        """Тест форматирования когда часть дней свободна"""
        result = _format_availability_response(availability_period_partial, "март")

        assert "В март свободно 10 из 31 дней" in result
        assert "Свободные даты:" in result
        assert "Хотите забронировать одну из свободных дат?" in result

    def test_format_no_free(self, availability_period_no_free):
        """Тест форматирования когда нет свободных дней"""
        result = _format_availability_response(availability_period_no_free, "март")

        assert "К сожалению, на март нет свободных дней" in result
        assert "Попробуйте выбрать другие даты" in result

    def test_format_many_free_dates_truncated(self):
        """Тест что при большом количестве свободных дат список обрезается"""
        now = datetime.now(TZ)
        # Создаем 15 свободных дней из 20
        slots = []
        for i in range(20):
            slots.append(
                AvailabilitySlot(
                    date=now + timedelta(days=i),
                    is_available=i < 15,  # Первые 15 дней свободны
                )
            )

        availability_period = AvailabilityPeriod(
            start_date=now, end_date=now, slots=slots, total_available_days=15
        )

        result = _format_availability_response(availability_period, "март")

        # Поскольку свободных дат больше 10, они не должны показываться в списке
        assert "В март свободно 15 из 20 дней" in result
        assert "Свободные даты:" not in result
