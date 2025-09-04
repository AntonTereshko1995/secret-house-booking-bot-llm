"""
Unit tests for PricingExtractor
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from domain.booking.pricing import PricingRequest
from infrastructure.llm.extractors.pricing_extractor import PricingExtractor


class TestPricingExtractor:
    """Tests for PricingExtractor"""

    @pytest.fixture
    def extractor(self):
        """Create PricingExtractor instance with mocked DateExtractor"""
        with patch("infrastructure.llm.extractors.pricing_extractor.DateExtractor"):
            return PricingExtractor()

    @pytest.mark.asyncio
    async def test_extract_pricing_requirements_basic(self, extractor):
        """Test basic pricing requirements extraction"""
        text = "сколько стоит суточный тариф"

        request = await extractor.extract_pricing_requirements(text)

        assert isinstance(request, PricingRequest)
        assert request.tariff == "суточно от 3 человек"  # Default suточный
        assert request.add_ons == []

    @pytest.mark.asyncio
    async def test_extract_pricing_requirements_with_guests(self, extractor):
        """Test extraction with guest count"""
        text = "цена на 4 человека суточный тариф"

        request = await extractor.extract_pricing_requirements(text)

        assert request.number_guests == 4
        assert request.tariff == "суточно от 3 человек"

    @pytest.mark.asyncio
    async def test_extract_pricing_requirements_with_addons(self, extractor):
        """Test extraction with add-ons"""
        text = "стоимость суточного тарифа с сауной и фотосъемкой"

        request = await extractor.extract_pricing_requirements(text)

        assert "sauna" in request.add_ons
        assert "photoshoot" in request.add_ons
        assert len(request.add_ons) == 2

    def test_extract_tariff_daily_for_couple(self, extractor):
        """Test tariff extraction for couple"""
        tariff = extractor._extract_tariff("суточный тариф для двоих")
        assert tariff == "суточно для двоих"

        tariff = extractor._extract_tariff("daily for 2 people")
        assert tariff == "суточно для двоих"

    def test_extract_tariff_daily_for_group(self, extractor):
        """Test tariff extraction for group"""
        tariff = extractor._extract_tariff("суточный тариф от 3 человек")
        assert tariff == "суточно от 3 человек"

        tariff = extractor._extract_tariff("daily for 3 people")
        assert tariff == "суточно от 3 человек"

    def test_extract_tariff_12_hours(self, extractor):
        """Test 12-hour tariff extraction"""
        tariff = extractor._extract_tariff("12 часов")
        assert tariff == "12 часов"

        tariff = extractor._extract_tariff("полсуток")
        assert tariff == "12 часов"

        tariff = extractor._extract_tariff("12 hours")
        assert tariff == "12 часов"

    def test_extract_tariff_working(self, extractor):
        """Test working hours tariff extraction"""
        tariff = extractor._extract_tariff("рабочий тариф")
        assert tariff == "рабочий"

        tariff = extractor._extract_tariff("working hours")
        assert tariff == "рабочий"

    def test_extract_tariff_incognito(self, extractor):
        """Test incognito tariff extraction"""
        tariff = extractor._extract_tariff("инкогнито на день")
        assert tariff == "инкогнито день"

        tariff = extractor._extract_tariff("инкогнито 12 часов")
        assert tariff == "инкогнито 12"

    def test_extract_tariff_subscription(self, extractor):
        """Test subscription tariff extraction"""
        tariff = extractor._extract_tariff("абонемент на 3 посещения")
        assert tariff == "абонемент 3"

        tariff = extractor._extract_tariff("абонемент на 5 посещений")
        assert tariff == "абонемент 5"

        tariff = extractor._extract_tariff("subscription")
        assert tariff == "абонемент 3"  # Default

    def test_extract_tariff_general_keywords(self, extractor):
        """Test tariff extraction with general keywords"""
        # Should default to group tariff
        tariff = extractor._extract_tariff("суточная аренда")
        assert tariff == "суточно от 3 человек"

        # Should detect couple tariff
        tariff = extractor._extract_tariff("суточная аренда для двоих")
        assert tariff == "суточно для двоих"

        # Should detect 12-hour tariff
        tariff = extractor._extract_tariff("аренда на полсуток")
        assert tariff == "12 часов"

    def test_extract_addons_sauna(self, extractor):
        """Test sauna add-on extraction"""
        addons = extractor._extract_addons("с сауной")
        assert "sauna" in addons

        addons = extractor._extract_addons("with sauna")
        assert "sauna" in addons

    def test_extract_addons_photoshoot(self, extractor):
        """Test photoshoot add-on extraction"""
        addons = extractor._extract_addons("с фотосъемкой")
        assert "photoshoot" in addons

        addons = extractor._extract_addons("с фотосессией")
        assert "photoshoot" in addons

        addons = extractor._extract_addons("with photography")
        assert "photoshoot" in addons

    def test_extract_addons_secret_room(self, extractor):
        """Test secret room add-on extraction"""
        addons = extractor._extract_addons("с секретной комнатой")
        assert "secret_room" in addons

        addons = extractor._extract_addons("with secret room")
        assert "secret_room" in addons

    def test_extract_addons_second_bedroom(self, extractor):
        """Test second bedroom add-on extraction"""
        addons = extractor._extract_addons("со второй спальней")
        assert "second_bedroom" in addons

        addons = extractor._extract_addons("with second bedroom")
        assert "second_bedroom" in addons

    def test_extract_addons_multiple(self, extractor):
        """Test multiple add-ons extraction"""
        text = "с сауной, фотосъемкой и секретной комнатой"
        addons = extractor._extract_addons(text)

        assert "sauna" in addons
        assert "photoshoot" in addons
        assert "secret_room" in addons
        assert len(addons) == 3

    def test_extract_guest_count_numbers(self, extractor):
        """Test guest count extraction with numbers"""
        assert extractor._extract_guest_count("на 3 человека") == 3
        assert extractor._extract_guest_count("для 5 людей") == 5
        assert extractor._extract_guest_count("4 guests") == 4

    def test_extract_guest_count_words(self, extractor):
        """Test guest count extraction with words"""
        assert extractor._extract_guest_count("для двоих") == 2
        assert extractor._extract_guest_count("для троих") == 3
        assert extractor._extract_guest_count("для четырех человек") == 4

    def test_extract_guest_count_special_cases(self, extractor):
        """Test guest count extraction special cases"""
        assert extractor._extract_guest_count("для одного") == 1
        assert extractor._extract_guest_count("для пары") == 2
        assert extractor._extract_guest_count("для компании") == 4
        assert extractor._extract_guest_count("single person") == 1
        assert extractor._extract_guest_count("couple") == 2

    def test_extract_guest_count_no_match(self, extractor):
        """Test guest count extraction when no match"""
        assert extractor._extract_guest_count("просто аренда") is None

    @patch("infrastructure.llm.extractors.pricing_extractor.DateExtractor")
    def test_extract_time_parameters_with_dates(
        self, mock_date_extractor_class, extractor
    ):
        """Test time parameters extraction with dates"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_date_extractor_class.return_value = mock_extractor

        start_date = datetime(2025, 3, 15, 14, 0)
        end_date = datetime(2025, 3, 17, 12, 0)
        mock_extractor.extract_dates_from_text.return_value = (
            start_date,
            end_date,
            "15-17 марта",
        )

        # Create new extractor to use mock
        extractor = PricingExtractor()

        duration_days, extracted_start, extracted_end = (
            extractor._extract_time_parameters("с 15 по 17 марта")
        )

        assert duration_days == 2
        assert extracted_start == start_date
        assert extracted_end == end_date

    def test_extract_time_parameters_duration_words(self, extractor):
        """Test duration extraction from text"""
        duration_days, _, _ = extractor._extract_time_parameters("на 3 дня")
        assert duration_days == 3

        duration_days, _, _ = extractor._extract_time_parameters("на один день")
        assert duration_days == 1

        duration_days, _, _ = extractor._extract_time_parameters("на неделю")
        assert duration_days == 7

    def test_is_pricing_query_positive(self, extractor):
        """Test positive pricing query detection"""
        assert extractor.is_pricing_query("сколько стоит") is True
        assert extractor.is_pricing_query("какие цены") is True
        assert extractor.is_pricing_query("стоимость аренды") is True
        assert extractor.is_pricing_query("прайс-лист") is True
        assert extractor.is_pricing_query("how much") is True
        assert extractor.is_pricing_query("what's the price") is True
        assert extractor.is_pricing_query("pricing information") is True

    def test_is_pricing_query_negative(self, extractor):
        """Test negative pricing query detection"""
        assert extractor.is_pricing_query("хочу забронировать") is False
        assert extractor.is_pricing_query("какие даты свободны") is False
        assert extractor.is_pricing_query("как добраться") is False

    def test_extract_comparison_request_positive(self, extractor):
        """Test comparison request detection"""
        assert extractor.extract_comparison_request("сравни тарифы") is True
        assert extractor.extract_comparison_request("какой тариф лучше") is True
        assert extractor.extract_comparison_request("что лучше выбрать") is True
        assert extractor.extract_comparison_request("compare prices") is True
        assert extractor.extract_comparison_request("what's the difference") is True

    def test_extract_comparison_request_negative(self, extractor):
        """Test non-comparison request detection"""
        assert extractor.extract_comparison_request("сколько стоит суточный") is False
        assert extractor.extract_comparison_request("цена 12 часов") is False

    @pytest.mark.asyncio
    async def test_extract_pricing_requirements_error_handling(self, extractor):
        """Test error handling in extraction"""
        # Mock date extractor to raise exception
        extractor.date_extractor.extract_dates_from_text = MagicMock(
            side_effect=Exception("Test error")
        )

        text = "сколько стоит аренда на завтра"
        request = await extractor.extract_pricing_requirements(text)

        # Should not crash and return basic request
        assert isinstance(request, PricingRequest)
        # Date extraction failed but basic parsing should work
        assert request.duration_days is None

    @pytest.mark.asyncio
    async def test_extract_pricing_requirements_complex(self, extractor):
        """Test complex pricing requirements extraction"""
        text = "сколько стоит суточный тариф для двоих на 3 дня с сауной и фотосъемкой для 2 человек"

        request = await extractor.extract_pricing_requirements(text)

        assert request.tariff == "суточно для двоих"
        assert request.number_guests == 2
        assert request.duration_days == 3
        assert "sauna" in request.add_ons
        assert "photoshoot" in request.add_ons
