"""
Integration tests for complete pricing flow
"""

import json
from unittest.mock import mock_open, patch

import pytest

from infrastructure.llm.graphs.app.app_graph_builder import build_app_graph


class TestPricingFlowIntegration:
    """Integration tests for pricing flow through LangGraph"""

    @pytest.fixture
    def mock_pricing_config(self):
        """Mock pricing configuration for tests"""
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
    def app_graph(self, mock_pricing_config):
        """Create app graph with mocked pricing config"""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(mock_pricing_config))
        ):
            with patch("pathlib.Path.exists", return_value=True):
                return build_app_graph()

    @pytest.mark.asyncio
    async def test_basic_pricing_query_russian(self, app_graph):
        """Test basic pricing query in Russian"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "сколько стоит суточный тариф от 3 человек",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_thread_1"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "💰" in result["reply"]
        assert "700 руб" in result["reply"]
        assert "от 3 человек" in result["reply"]
        assert "pricing_data" in result

    @pytest.mark.asyncio
    async def test_pricing_query_with_addons_russian(self, app_graph):
        """Test pricing query with add-ons in Russian"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "стоимость 12-часового тарифа с сауной и секретной комнатой",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_thread_2"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "💰" in result["reply"]
        # Base (250) + Sauna (100) + Secret room (70) = 420
        assert "420 руб" in result["reply"]
        assert "Сауна" in result["reply"]
        assert "Секретная комната" in result["reply"]

    @pytest.mark.asyncio
    async def test_pricing_query_couple_tariff_russian(self, app_graph):
        """Test pricing query for couple tariff in Russian"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "цена суточного тарифа для двоих на 2 дня",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_thread_3"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "💰" in result["reply"]
        assert "900 руб" in result["reply"]  # Multi-day price for 2 days
        assert "для двоих" in result["reply"]
        assert "(2 дн.)" in result["reply"]

    @pytest.mark.asyncio
    async def test_pricing_query_english(self, app_graph):
        """Test pricing query in English"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "how much does daily tariff for 3 people cost",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_thread_4"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "💰" in result["reply"]
        assert "700 руб" in result["reply"]

    @pytest.mark.asyncio
    async def test_general_pricing_inquiry_russian(self, app_graph):
        """Test general pricing inquiry in Russian"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "какие у вас цены",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_thread_5"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "📋 **Доступные тарифы:**" in result["reply"]
        assert "12 часов" in result["reply"]
        assert "Суточно" in result["reply"]
        assert "точного расчета" in result["reply"]

    @pytest.mark.asyncio
    async def test_tariff_comparison_request_russian(self, app_graph):
        """Test tariff comparison request in Russian"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "сравните тарифы",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_thread_6"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "📋 **Доступные тарифы:**" in result["reply"]
        assert "конкретной стоимости" in result["reply"]
        assert result["pricing_data"]["type"] == "comparison"

    @pytest.mark.asyncio
    async def test_router_price_intent_detection(self, app_graph):
        """Test that router correctly detects price intent"""
        pricing_queries = [
            "сколько стоит",
            "какая цена",
            "стоимость аренды",
            "прайс-лист",
            "тариф",
            "how much",
            "price",
            "cost",
        ]

        for query in pricing_queries:
            initial_state = {"user_id": 123, "text": query}
            config = {"configurable": {"thread_id": f"test_router_{hash(query)}"}}

            result = await app_graph.ainvoke(initial_state, config)

            assert result["intent"] == "price", f"Failed for query: {query}"

    @pytest.mark.asyncio
    async def test_pricing_state_persistence(self, app_graph):
        """Test that pricing data is properly stored in state"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "сколько стоит суточный тариф от 3 человек на 3 дня",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_persistence"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Check state structure
        assert "pricing_data" in result
        pricing_data = result["pricing_data"]

        assert "breakdown" in pricing_data
        assert "request" in pricing_data
        assert "valid_until" in pricing_data

        # Check breakdown details
        breakdown = pricing_data["breakdown"]
        assert breakdown["tariff_id"] == 1
        assert breakdown["duration_days"] == 3
        assert breakdown["total_cost"] == "1850"  # Multi-day price

    @pytest.mark.asyncio
    async def test_pricing_error_handling_unknown_tariff(self, app_graph):
        """Test error handling for unknown tariff"""
        # Test input with non-existent tariff
        initial_state = {
            "user_id": 123,
            "text": "цена несуществующего тарифа",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_error_1"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Should handle gracefully, not crash
        assert "reply" in result
        assert result["intent"] == "price"
        # Should show available tariffs when can't find specific one
        assert "📋" in result["reply"] or "💡" in result["reply"]

    @pytest.mark.asyncio
    async def test_complex_pricing_query_with_all_parameters(self, app_graph):
        """Test complex pricing query with all parameters"""
        # Test input
        initial_state = {
            "user_id": 123,
            "text": "сколько стоит суточный тариф для двоих на 2 дня с сауной и фотосъемкой для 2 человек",
        }

        # Execute graph
        config = {"configurable": {"thread_id": "test_complex"}}
        result = await app_graph.ainvoke(initial_state, config)

        # Assertions
        assert "reply" in result
        assert result["intent"] == "price"
        assert "💰" in result["reply"]

        # Check that all components are reflected
        assert "для двоих" in result["reply"]
        assert "(2 дн.)" in result["reply"]

        # Check pricing data contains extracted parameters
        pricing_data = result["pricing_data"]
        request_data = pricing_data["request"]

        # Should extract couple tariff, 2 days, and add-ons
        assert "двоих" in request_data.get("tariff", "")
        assert request_data.get("duration_days") == 2

    @pytest.mark.asyncio
    async def test_pricing_flow_thread_isolation(self, app_graph):
        """Test that different threads maintain separate state"""
        # First thread
        state1 = {"user_id": 123, "text": "цена суточного тарифа"}
        config1 = {"configurable": {"thread_id": "thread_1"}}
        result1 = await app_graph.ainvoke(state1, config1)

        # Second thread
        state2 = {"user_id": 456, "text": "стоимость 12-часового тарифа"}
        config2 = {"configurable": {"thread_id": "thread_2"}}
        result2 = await app_graph.ainvoke(state2, config2)

        # Results should be different and specific to each query
        assert result1["intent"] == "price"
        assert result2["intent"] == "price"
        assert "суточн" in result1["reply"]
        assert "12 час" in result2["reply"]

        # Should have different pricing data
        assert result1["pricing_data"] != result2["pricing_data"]
