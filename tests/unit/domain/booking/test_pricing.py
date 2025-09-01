"""
Unit tests for pricing domain models
"""

from datetime import datetime
from decimal import Decimal

from domain.booking.pricing import (
    AddOnService,
    PricingBreakdown,
    PricingRequest,
    PricingResponse,
    TariffRate,
)


class TestTariffRate:
    """Tests for TariffRate model"""

    def test_create_tariff_rate(self):
        """Test creating a tariff rate"""
        tariff = TariffRate(
            tariff=1,
            name="тест тариф",
            duration_hours=24,
            price=Decimal("500"),
            sauna_price=Decimal("100"),
            secret_room_price=Decimal("70"),
            second_bedroom_price=Decimal("70"),
            extra_hour_price=Decimal("30"),
            extra_people_price=Decimal("0"),
            photoshoot_price=Decimal("100"),
            max_people=6,
            is_check_in_time_limit=False,
            is_photoshoot=True,
            is_transfer=False,
            subscription_type=0,
            multi_day_prices={"1": Decimal("500"), "2": Decimal("900")},
        )

        assert tariff.tariff == 1
        assert tariff.name == "тест тариф"
        assert tariff.duration_hours == 24
        assert tariff.price == Decimal("500")
        assert tariff.max_people == 6
        assert "1" in tariff.multi_day_prices
        assert tariff.multi_day_prices["1"] == Decimal("500")

    def test_tariff_rate_defaults(self):
        """Test TariffRate with default values"""
        tariff = TariffRate(
            tariff=1,
            name="тест",
            duration_hours=12,
            price=Decimal("200"),
            sauna_price=Decimal("0"),
            secret_room_price=Decimal("0"),
            second_bedroom_price=Decimal("0"),
            extra_hour_price=Decimal("30"),
            extra_people_price=Decimal("0"),
            photoshoot_price=Decimal("0"),
            max_people=2,
            is_check_in_time_limit=True,
            is_photoshoot=False,
            is_transfer=False,
            subscription_type=0,
        )

        assert tariff.multi_day_prices == {}


class TestAddOnService:
    """Tests for AddOnService model"""

    def test_create_addon_service(self):
        """Test creating an add-on service"""
        service = AddOnService(
            service_id="sauna",
            name="Сауна",
            price=Decimal("100"),
            is_per_hour=False,
            description="Сауна для отдыха",
        )

        assert service.service_id == "sauna"
        assert service.name == "Сауна"
        assert service.price == Decimal("100")
        assert service.is_per_hour is False
        assert service.description == "Сауна для отдыха"

    def test_addon_service_per_hour(self):
        """Test add-on service with per-hour pricing"""
        service = AddOnService(
            service_id="extra_time",
            name="Дополнительное время",
            price=Decimal("30"),
            is_per_hour=True,
            description="Дополнительные часы аренды",
        )

        assert service.is_per_hour is True


class TestPricingRequest:
    """Tests for PricingRequest model"""

    def test_create_pricing_request_basic(self):
        """Test creating basic pricing request"""
        request = PricingRequest()

        assert request.tariff is None
        assert request.tariff_id is None
        assert request.add_ons == []
        assert request.number_guests is None

    def test_create_pricing_request_full(self):
        """Test creating full pricing request"""
        start_date = datetime(2025, 3, 15, 14, 0)
        end_date = datetime(2025, 3, 17, 12, 0)

        request = PricingRequest(
            tariff="суточно от 3 человек",
            tariff_id=1,
            start_date=start_date,
            end_date=end_date,
            duration_hours=24,
            duration_days=2,
            add_ons=["sauna", "photoshoot"],
            number_guests=4,
            is_weekend=True,
        )

        assert request.tariff == "суточно от 3 человек"
        assert request.tariff_id == 1
        assert request.duration_days == 2
        assert len(request.add_ons) == 2
        assert "sauna" in request.add_ons
        assert request.number_guests == 4

    def test_pricing_request_json_encoding(self):
        """Test JSON encoding of PricingRequest"""
        start_date = datetime(2025, 3, 15, 14, 0)
        request = PricingRequest(start_date=start_date)

        # Should not raise an error during serialization
        data = request.dict()
        assert "start_date" in data


class TestPricingBreakdown:
    """Tests for PricingBreakdown model"""

    def test_create_pricing_breakdown(self):
        """Test creating pricing breakdown"""
        breakdown = PricingBreakdown(
            tariff_name="тест тариф",
            tariff_id=1,
            base_cost=Decimal("500"),
            duration_hours=24,
            duration_days=2,
            add_on_costs={"Сауна": Decimal("100"), "Фотосъемка": Decimal("100")},
            total_cost=Decimal("700"),
            max_people=6,
            includes_transfer=True,
            includes_photoshoot=False,
        )

        assert breakdown.tariff_name == "тест тариф"
        assert breakdown.tariff_id == 1
        assert breakdown.base_cost == Decimal("500")
        assert breakdown.duration_days == 2
        assert breakdown.total_cost == Decimal("700")
        assert breakdown.currency == "RUB"
        assert breakdown.includes_transfer is True
        assert len(breakdown.add_on_costs) == 2

    def test_pricing_breakdown_defaults(self):
        """Test PricingBreakdown with default values"""
        breakdown = PricingBreakdown(
            tariff_name="тест",
            tariff_id=1,
            base_cost=Decimal("200"),
            duration_hours=12,
            total_cost=Decimal("200"),
            max_people=2,
        )

        assert breakdown.duration_days == 1
        assert breakdown.currency == "RUB"
        assert breakdown.add_on_costs == {}
        assert breakdown.includes_transfer is False
        assert breakdown.includes_photoshoot is False


class TestPricingResponse:
    """Tests for PricingResponse model"""

    def test_create_pricing_response(self):
        """Test creating full pricing response"""
        breakdown = PricingBreakdown(
            tariff_name="тест тариф",
            tariff_id=1,
            base_cost=Decimal("500"),
            duration_hours=24,
            total_cost=Decimal("600"),
            max_people=4,
        )

        valid_until = datetime(2025, 3, 16, 14, 0)
        response = PricingResponse(
            breakdown=breakdown,
            formatted_message="💰 Стоимость: 600 руб.",
            booking_suggestion="Хотите забронировать?",
            valid_until=valid_until,
        )

        assert response.breakdown.total_cost == Decimal("600")
        assert "💰" in response.formatted_message
        assert "забронировать" in response.booking_suggestion
        assert response.valid_until == valid_until

    def test_pricing_response_json_encoding(self):
        """Test JSON encoding of PricingResponse"""
        breakdown = PricingBreakdown(
            tariff_name="тест",
            tariff_id=1,
            base_cost=Decimal("200"),
            duration_hours=12,
            total_cost=Decimal("200"),
            max_people=2,
        )

        response = PricingResponse(
            breakdown=breakdown,
            formatted_message="тест",
            booking_suggestion="тест",
            valid_until=datetime(2025, 3, 16),
        )

        # Should not raise an error during serialization
        data = response.dict()
        assert "breakdown" in data
        assert "valid_until" in data
