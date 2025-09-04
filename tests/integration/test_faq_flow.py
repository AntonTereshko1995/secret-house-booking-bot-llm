"""
Integration tests for FAQ flow through LangGraph
"""

from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.llm.graphs.app.app_graph_builder import build_app_graph
from infrastructure.llm.graphs.common.graph_state import AppState


class TestFAQFlow:
    """Integration tests for complete FAQ flow"""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for integration tests"""
        mock_response = AsyncMock()
        mock_response.content = "🏠 The Secret House предлагает уникальные возможности! У нас есть зеленая и белая спальни с современным дизайном, сауна и секретная комната. Для бронирования перейдите в пункт меню 'Забронировать'!"
        return mock_response

    @pytest.mark.asyncio
    async def test_faq_flow_routing_from_router(self, mock_llm_response):
        """Test complete FAQ flow from router to response"""

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm

            # Build the app graph
            app_graph = build_app_graph()

            # Initial state with FAQ question
            initial_state = AppState(
                user_id=12345, text="что есть в доме?", intent="unknown"
            )

            # Run the graph
            config = {"configurable": {"thread_id": "test-thread"}}
            final_state = await app_graph.ainvoke(initial_state, config)

            # Check routing worked correctly
            assert final_state["intent"] == "faq"
            assert "reply" in final_state
            assert len(final_state["reply"]) > 0
            assert "faq_data" in final_state

            # Check that LLM was called
            mock_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_faq_flow_multiple_questions(self, mock_llm_response):
        """Test FAQ flow with multiple questions in conversation"""

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm

            app_graph = build_app_graph()
            config = {"configurable": {"thread_id": "test-conversation"}}

            # First question
            state1 = AppState(
                user_id=12345, text="какие комнаты есть?", intent="unknown"
            )

            result1 = await app_graph.ainvoke(state1, config)
            assert result1["intent"] == "faq"
            assert "faq_context" in result1

            # Second question - should maintain context
            state2 = AppState(
                user_id=12345,
                text="а сколько это стоит?",
                intent="unknown",
                faq_context=result1["faq_context"],
            )

            result2 = await app_graph.ainvoke(state2, config)
            assert result2["intent"] == "faq"

            # Context should be updated
            context = result2["faq_context"]
            assert context["total_questions"] >= 2

    @pytest.mark.asyncio
    async def test_faq_flow_intent_detection_patterns(self, mock_llm_response):
        """Test FAQ intent detection with various question patterns"""

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm

            app_graph = build_app_graph()

            # Test different FAQ question patterns
            faq_questions = [
                "что есть в доме?",
                "какие удобства включены?",
                "как добраться до дома?",
                "где находится дом?",
                "можно ли курить?",
                "расскажи о доме",
                "what is included?",
                "how does it work?",
            ]

            for question in faq_questions:
                state = AppState(user_id=12345, text=question, intent="unknown")

                config = {"configurable": {"thread_id": f"test-{hash(question)}"}}
                result = await app_graph.ainvoke(state, config)

                # All should route to FAQ
                assert result["intent"] == "faq", (
                    f"Question '{question}' should route to FAQ"
                )
                assert "reply" in result

    @pytest.mark.asyncio
    async def test_faq_flow_not_routing_non_faq(self, mock_llm_response):
        """Test that non-FAQ questions don't route to FAQ"""

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm

            app_graph = build_app_graph()

            # Test questions that should NOT route to FAQ
            non_faq_questions = [
                ("забронировать дом", "booking"),
                ("свободные даты", "availability"),
                ("сколько стоит аренда", "price"),
                ("изменить бронирование", "change"),
            ]

            for question, expected_intent in non_faq_questions:
                state = AppState(user_id=12345, text=question, intent="unknown")

                config = {"configurable": {"thread_id": f"test-{hash(question)}"}}
                result = await app_graph.ainvoke(state, config)

                # Should route to correct intent, not FAQ
                assert result["intent"] == expected_intent, (
                    f"Question '{question}' should route to {expected_intent}, not FAQ"
                )

    @pytest.mark.asyncio
    async def test_faq_flow_state_persistence(self, mock_llm_response):
        """Test FAQ state persistence in graph memory"""

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm

            app_graph = build_app_graph()
            thread_id = "persistent-test"
            config = {"configurable": {"thread_id": thread_id}}

            # First interaction
            state1 = AppState(
                user_id=12345, text="что включено в аренду?", intent="unknown"
            )

            result1 = await app_graph.ainvoke(state1, config)
            assert "faq_context" in result1

            # Get current state from memory
            current_state = await app_graph.aget_state(config)
            assert current_state is not None

            # Second interaction with same thread
            state2 = AppState(user_id=12345, text="а есть ли сауна?", intent="unknown")

            result2 = await app_graph.ainvoke(state2, config)

            # Should maintain conversation context
            context = result2["faq_context"]
            assert context["total_questions"] >= 2

    @pytest.mark.asyncio
    async def test_faq_flow_error_recovery(self):
        """Test FAQ flow error recovery when LLM fails"""

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("LLM API error")
            mock_get_llm.return_value = mock_llm

            app_graph = build_app_graph()

            state = AppState(user_id=12345, text="что есть в доме?", intent="unknown")

            config = {"configurable": {"thread_id": "error-test"}}
            result = await app_graph.ainvoke(state, config)

            # Should still route to FAQ and handle error gracefully
            assert result["intent"] == "faq"
            assert "reply" in result
            assert (
                "@the_secret_house" in result["reply"]
            )  # Error message includes admin contact

    @pytest.mark.asyncio
    async def test_faq_flow_performance(self, mock_llm_response):
        """Test FAQ flow performance metrics"""
        import time

        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm

            app_graph = build_app_graph()

            start_time = time.time()

            state = AppState(
                user_id=12345, text="расскажи о доме подробнее", intent="unknown"
            )

            config = {"configurable": {"thread_id": "performance-test"}}
            result = await app_graph.ainvoke(state, config)

            end_time = time.time()
            total_time = end_time - start_time

            assert result["intent"] == "faq"
            assert "faq_data" in result

            # Performance should be reasonable (adjust threshold as needed)
            assert total_time < 10.0  # Should complete within 10 seconds
