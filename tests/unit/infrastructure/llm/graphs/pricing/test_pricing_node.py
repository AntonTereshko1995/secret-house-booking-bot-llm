"""
Unit tests for pricing_node
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from domain.booking.pricing import PricingBreakdown, PricingRequest, PricingResponse
from infrastructure.llm.graphs.pricing.pricing_node import pricing_node

TZ = ZoneInfo("Europe/Minsk")


class TestPricingNode:
    """Tests for pricing_node function"""

    @pytest.fixture
    def mock_pricing_service(self):
        """Mock PricingService"""
        service = MagicMock()
        service.calculate_pricing = AsyncMock()
        service.get_tariffs_summary = AsyncMock()
        return service

    @pytest.fixture
    def mock_pricing_extractor(self):
        """Mock PricingExtractor"""
        extractor = MagicMock()
        extractor.extract_pricing_requirements = AsyncMock()
        extractor.is_pricing_query = MagicMock()
        extractor.extract_comparison_request = MagicMock()
        return extractor

    @pytest.fixture
    def sample_pricing_response(self):
        """Sample pricing response"""
        breakdown = PricingBreakdown(
            tariff_name="тест тариф",
            tariff_id=1,
            base_cost=Decimal("500"),
            duration_hours=24,
            total_cost=Decimal("600"),
            max_people=4,
        )

        return PricingResponse(
            breakdown=breakdown,
            formatted_message="💰 Стоимость: 600 руб.",
            booking_suggestion="Хотите забронировать?",
            valid_until=datetime.now(TZ) + timedelta(hours=24),
        )

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_basic_request(
        self, mock_extractor, mock_service, sample_pricing_response
    ):
        """Test basic pricing node request"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest(
            tariff="суточно от 3 человек", duration_days=1
        )
        mock_service.calculate_pricing.return_value = sample_pricing_response

        # Test
        state = {"text": "сколько стоит суточный тариф"}
        result = await pricing_node(state)

        # Assertions
        assert result["intent"] == "price"
        assert "💰" in result["reply"]
        assert "600 руб" in result["reply"]
        assert "Хотите забронировать?" in result["reply"]
        assert "pricing_data" in result
        mock_service.calculate_pricing.assert_called_once()

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_comparison_request(self, mock_extractor, mock_service):
        """Test pricing node with comparison request"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = True
        mock_service.get_tariffs_summary.return_value = (
            "📋 Доступные тарифы:\n• Тариф 1: 500 руб."
        )

        # Test
        state = {"text": "сравни тарифы"}
        result = await pricing_node(state)

        # Assertions
        assert result["intent"] == "price"
        assert "📋 Доступные тарифы:" in result["reply"]
        assert "конкретной стоимости" in result["reply"]
        assert result["pricing_data"]["type"] == "comparison"
        mock_service.get_tariffs_summary.assert_called_once()

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_general_inquiry(self, mock_extractor, mock_service):
        """Test pricing node with general price inquiry"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = (
            PricingRequest()
        )  # No specific tariff
        mock_extractor.is_pricing_query.return_value = True
        mock_service.get_tariffs_summary.return_value = (
            "📋 Доступные тарифы:\n• Тариф 1"
        )

        # Test
        state = {"text": "какие цены"}
        result = await pricing_node(state)

        # Assertions
        assert result["intent"] == "price"
        assert "📋 Доступные тарифы:" in result["reply"]
        assert "точного расчета" in result["reply"]
        assert "Например:" in result["reply"]
        assert result["pricing_data"]["type"] == "general_inquiry"

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_validation_error(self, mock_extractor, mock_service):
        """Test pricing node with validation error"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest(
            tariff="неизвестный тариф"
        )
        mock_service.calculate_pricing.side_effect = ValueError("Неизвестный тариф")
        mock_service.get_tariffs_summary.return_value = (
            "📋 Доступные тарифы:\n• Тариф 1"
        )

        # Test
        state = {"text": "цена неизвестного тарифа"}
        result = await pricing_node(state)

        # Assertions
        assert result["intent"] == "price"
        assert "⚠️" in result["reply"]
        assert "не удалось найти" in result["reply"]
        assert "📋 Доступные тарифы:" in result["reply"]
        assert result["error"] == "unknown_tariff"

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_general_error(self, mock_extractor, mock_service):
        """Test pricing node with general error"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest(
            tariff="суточно от 3 человек"
        )
        mock_service.calculate_pricing.side_effect = Exception("Database error")

        # Test
        state = {"text": "сколько стоит суточный тариф"}
        result = await pricing_node(state)

        # Assertions
        assert result["intent"] == "price"
        assert "😔" in result["reply"]
        assert "ошибка при расчете" in result["reply"]
        assert "Пример корректного запроса:" in result["reply"]
        assert "error" in result
        assert result["error"] == "Database error"

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_empty_text(self, mock_extractor, mock_service):
        """Test pricing node with empty text"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest()
        mock_extractor.is_pricing_query.return_value = False

        # Test
        state = {"text": ""}
        result = await pricing_node(state)

        # Should handle gracefully and not crash
        assert result["intent"] == "price"

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_complex_request(
        self, mock_extractor, mock_service, sample_pricing_response
    ):
        """Test pricing node with complex request"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest(
            tariff="суточно для двоих",
            duration_days=3,
            add_ons=["sauna", "photoshoot"],
            number_guests=2,
        )
        mock_service.calculate_pricing.return_value = sample_pricing_response

        # Test
        state = {
            "text": "сколько стоит суточный тариф для двоих на 3 дня с сауной и фотосессией"
        }
        result = await pricing_node(state)

        # Assertions
        assert result["intent"] == "price"
        assert "reply" in result
        assert "pricing_data" in result

        # Check that complex request was passed to service
        call_args = mock_service.calculate_pricing.call_args[0][0]
        assert call_args.tariff == "суточно для двоих"
        assert call_args.duration_days == 3
        assert "sauna" in call_args.add_ons
        assert call_args.number_guests == 2

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_pricing_data_structure(
        self, mock_extractor, mock_service, sample_pricing_response
    ):
        """Test pricing node returns correct pricing data structure"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest(
            tariff="суточно от 3 человек"
        )
        mock_service.calculate_pricing.return_value = sample_pricing_response

        # Test
        state = {"text": "сколько стоит суточный тариф"}
        result = await pricing_node(state)

        # Check pricing_data structure
        pricing_data = result["pricing_data"]
        assert "breakdown" in pricing_data
        assert "request" in pricing_data
        assert "valid_until" in pricing_data

        # Check breakdown data
        breakdown = pricing_data["breakdown"]
        assert breakdown["tariff_id"] == 1
        assert breakdown["total_cost"] == "600"
        assert breakdown["max_people"] == 4

    @pytest.mark.asyncio
    @patch("infrastructure.llm.graphs.pricing.pricing_node.logger")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_service")
    @patch("infrastructure.llm.graphs.pricing.pricing_node.pricing_extractor")
    async def test_pricing_node_logging(
        self, mock_extractor, mock_service, mock_logger, sample_pricing_response
    ):
        """Test pricing node logging"""
        # Setup mocks
        mock_extractor.extract_comparison_request.return_value = False
        mock_extractor.extract_pricing_requirements.return_value = PricingRequest(
            tariff="суточно от 3 человек"
        )
        mock_service.calculate_pricing.return_value = sample_pricing_response

        # Test
        state = {"text": "сколько стоит суточный тариф"}
        result = await pricing_node(state)

        # Check logging calls
        mock_logger.info.assert_called_once()
        mock_logger.debug.assert_called_once()

        # Check log content
        info_call = mock_logger.info.call_args
        assert "Processing pricing request" in info_call[0][0]
