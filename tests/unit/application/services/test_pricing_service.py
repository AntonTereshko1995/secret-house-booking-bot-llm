"""
Unit tests for PricingService
"""

import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, mock_open, patch
from zoneinfo import ZoneInfo

import pytest

from application.services.pricing_service import PricingService
from domain.booking.pricing import PricingRequest, TariffRate

TZ = ZoneInfo("Europe/Minsk")


class TestPricingService:
    """Tests for PricingService"""

    @pytest.fixture
    def mock_config_data(self):
        """Mock pricing configuration data"""
        return {
            "rental_prices": [
                {
                    "tariff": 1,
                    "name": "тариф 'Суточно' от 3 человек",
                    "duration_hours": 24,
                    "price": 700,
                    "sauna_price": 100,
                    "secret_room_price": 0,
                    "second_bedroom_price": 0,
                    "extra_hour_price": 30,
                    "extra_people_price": 0,
                    "photoshoot_price": 100,
                    "max_people": 6,
                    "is_check_in_time_limit": False,
                    "is_photoshoot": True,
                    "is_transfer": False,
                    "subscription_type": 0,
                    "multi_day_prices": {"1": 700, "2": 1300, "3": 1850},
                },
                {
                    "tariff": 7,
                    "name": "тариф 'Суточно' для двоих'",
                    "duration_hours": 24,
                    "price": 500,
                    "sauna_price": 100,
                    "secret_room_price": 0,
                    "second_bedroom_price": 0,
                    "extra_hour_price": 30,
                    "extra_people_price": 70,
                    "photoshoot_price": 100,
                    "max_people": 2,
                    "is_check_in_time_limit": False,
                    "is_photoshoot": True,
                    "is_transfer": False,
                    "subscription_type": 0,
                    "multi_day_prices": {"1": 500, "2": 900},
                },
                {
                    "tariff": 0,
                    "name": "тариф '12 часов'",
                    "duration_hours": 12,
                    "price": 250,
                    "sauna_price": 100,
                    "secret_room_price": 70,
                    "second_bedroom_price": 70,
                    "extra_hour_price": 30,
                    "extra_people_price": 70,
                    "photoshoot_price": 0,
                    "max_people": 2,
                    "is_check_in_time_limit": False,
                    "is_photoshoot": False,
                    "is_transfer": False,
                    "subscription_type": 0,
                    "multi_day_prices": {},
                },
            ]
        }

    @pytest.fixture
    def pricing_service(self, mock_config_data):
        """Create PricingService with mocked config"""
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                return PricingService()

    def test_load_tariff_rates(self, pricing_service):
        """Test loading tariff rates from config"""
        tariffs = pricing_service.tariff_rates

        assert len(tariffs) == 3
        assert 1 in tariffs
        assert 7 in tariffs
        assert 0 in tariffs

        # Check tariff 1
        tariff1 = tariffs[1]
        assert tariff1.name == "тариф 'Суточно' от 3 человек"
        assert tariff1.price == Decimal("700")
        assert tariff1.max_people == 6
        assert tariff1.duration_hours == 24

    def test_convert_prices_to_decimal(self, pricing_service):
        """Test price conversion to Decimal"""
        tariffs = pricing_service.tariff_rates
        tariff = tariffs[1]

        # All prices should be Decimal
        assert isinstance(tariff.price, Decimal)
        assert isinstance(tariff.sauna_price, Decimal)
        assert isinstance(tariff.multi_day_prices["1"], Decimal)

    @pytest.mark.asyncio
    async def test_calculate_pricing_basic(self, pricing_service):
        """Test basic pricing calculation"""
        request = PricingRequest(tariff_id=1, duration_days=1)

        response = await pricing_service.calculate_pricing(request)

        assert response.breakdown.tariff_id == 1
        assert response.breakdown.total_cost == Decimal("700")
        assert response.breakdown.duration_days == 1
        assert response.breakdown.max_people == 6
        assert "💰" in response.formatted_message

    @pytest.mark.asyncio
    async def test_calculate_pricing_multi_day(self, pricing_service):
        """Test multi-day pricing calculation"""
        request = PricingRequest(tariff_id=1, duration_days=2)

        response = await pricing_service.calculate_pricing(request)

        assert response.breakdown.duration_days == 2
        assert response.breakdown.total_cost == Decimal("1300")  # From multi_day_prices

    @pytest.mark.asyncio
    async def test_calculate_pricing_with_addons(self, pricing_service):
        """Test pricing calculation with add-ons"""
        request = PricingRequest(
            tariff_id=0,  # 12-hour tariff
            duration_days=1,
            add_ons=["sauna", "secret_room"],
        )

        response = await pricing_service.calculate_pricing(request)

        # Base price (250) + sauna (100) + secret_room (70) = 420
        assert response.breakdown.total_cost == Decimal("420")
        assert len(response.breakdown.add_on_costs) == 2
        assert "Сауна" in response.breakdown.add_on_costs
        assert "Секретная комната" in response.breakdown.add_on_costs

    @pytest.mark.asyncio
    async def test_calculate_pricing_with_dates(self, pricing_service):
        """Test pricing calculation with date range"""
        start_date = datetime(2025, 3, 15, 14, 0, tzinfo=TZ)
        end_date = datetime(2025, 3, 17, 12, 0, tzinfo=TZ)  # 2 days

        request = PricingRequest(
            tariff_id=1,
            start_date=start_date,
            end_date=end_date,
        )

        response = await pricing_service.calculate_pricing(request)

        assert response.breakdown.duration_days == 2
        assert response.breakdown.total_cost == Decimal("1300")

    @pytest.mark.asyncio
    async def test_get_tariff_for_request_by_id(self, pricing_service):
        """Test getting tariff by ID"""
        request = PricingRequest(tariff_id=1)

        tariff = await pricing_service._get_tariff_for_request(request)

        assert tariff is not None
        assert tariff.tariff == 1
        assert tariff.name == "тариф 'Суточно' от 3 человек"

    @pytest.mark.asyncio
    async def test_get_tariff_for_request_by_name(self, pricing_service):
        """Test getting tariff by name pattern"""
        request = PricingRequest(tariff="суточно для двоих")

        tariff = await pricing_service._get_tariff_for_request(request)

        assert tariff is not None
        assert tariff.tariff == 7
        assert "двоих" in tariff.name

    @pytest.mark.asyncio
    async def test_get_tariff_for_request_12_hours(self, pricing_service):
        """Test getting 12-hour tariff"""
        request = PricingRequest(tariff="12 часов")

        tariff = await pricing_service._get_tariff_for_request(request)

        assert tariff is not None
        assert tariff.tariff == 0
        assert "12 часов" in tariff.name

    @pytest.mark.asyncio
    async def test_get_tariff_for_request_default(self, pricing_service):
        """Test getting default tariff when no match"""
        request = PricingRequest()  # No tariff specified

        tariff = await pricing_service._get_tariff_for_request(request)

        assert tariff is not None
        assert tariff.tariff == 1  # Default to tariff 1

    def test_calculate_duration_days(self, pricing_service):
        """Test duration calculation"""
        # Test with duration_days specified
        request = PricingRequest(duration_days=3)
        tariff = MagicMock()

        result = pricing_service._calculate_duration_days(request, tariff)
        assert result == 3

        # Test with date range
        start_date = datetime(2025, 3, 15)
        end_date = datetime(2025, 3, 18)  # 3 days
        request = PricingRequest(start_date=start_date, end_date=end_date)

        result = pricing_service._calculate_duration_days(request, tariff)
        assert result == 3

        # Test default
        request = PricingRequest()
        result = pricing_service._calculate_duration_days(request, tariff)
        assert result == 1

    def test_calculate_base_cost_single_day(self, pricing_service):
        """Test base cost calculation for single day"""
        tariff = pricing_service.tariff_rates[1]

        cost = pricing_service._calculate_base_cost(tariff, 1)
        assert cost == Decimal("700")

    def test_calculate_base_cost_multi_day(self, pricing_service):
        """Test base cost calculation for multiple days"""
        tariff = pricing_service.tariff_rates[1]

        # Test exact match in multi_day_prices
        cost = pricing_service._calculate_base_cost(tariff, 2)
        assert cost == Decimal("1300")

        cost = pricing_service._calculate_base_cost(tariff, 3)
        assert cost == Decimal("1850")

    def test_format_pricing_message(self, pricing_service):
        """Test message formatting"""
        from domain.booking.pricing import PricingBreakdown

        breakdown = PricingBreakdown(
            tariff_name="тест тариф",
            tariff_id=1,
            base_cost=Decimal("500"),
            duration_hours=24,
            duration_days=2,
            add_on_costs={"Сауна": Decimal("100")},
            total_cost=Decimal("600"),
            max_people=4,
            includes_transfer=False,
            includes_photoshoot=False,
        )

        tariff = pricing_service.tariff_rates[1]
        message = pricing_service._format_pricing_message(breakdown, tariff)

        assert "💰" in message
        assert "тест тариф" in message
        assert "500 руб" in message
        assert "(2 дн.)" in message
        assert "4 чел." in message
        assert "Сауна: 100 руб" in message
        assert "600 руб" in message

    @pytest.mark.asyncio
    async def test_get_available_tariffs(self, pricing_service):
        """Test getting available tariffs"""
        tariffs = await pricing_service.get_available_tariffs()

        assert len(tariffs) == 3
        assert all(isinstance(t, TariffRate) for t in tariffs)

    @pytest.mark.asyncio
    async def test_get_tariff_by_id(self, pricing_service):
        """Test getting tariff by ID"""
        tariff = await pricing_service.get_tariff_by_id(1)

        assert tariff is not None
        assert tariff.tariff == 1

        # Test non-existent tariff
        tariff = await pricing_service.get_tariff_by_id(999)
        assert tariff is None

    @pytest.mark.asyncio
    async def test_get_tariffs_summary(self, pricing_service):
        """Test getting tariffs summary"""
        summary = await pricing_service.get_tariffs_summary()

        assert "📋 **Доступные тарифы:**" in summary
        assert "тариф '12 часов'" in summary
        assert "тариф 'Суточно'" in summary
        assert "Цена:" in summary
        assert "руб." in summary

    @pytest.mark.asyncio
    async def test_calculate_pricing_unknown_tariff(self, pricing_service):
        """Test error handling for unknown tariff"""
        request = PricingRequest(tariff_id=999)

        with pytest.raises(ValueError, match="Неизвестный тариф"):
            await pricing_service.calculate_pricing(request)

    def test_load_tariff_rates_file_not_found(self):
        """Test handling when config file doesn't exist"""
        with patch("pathlib.Path.exists", return_value=False):
            service = PricingService()
            assert service.tariff_rates == {}

    def test_load_tariff_rates_json_error(self):
        """Test handling JSON parsing errors"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("pathlib.Path.exists", return_value=True):
                service = PricingService()
                assert service.tariff_rates == {}
