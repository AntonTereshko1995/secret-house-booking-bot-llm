"""
Unit tests for FAQ LangGraph node
"""

from unittest.mock import AsyncMock, patch

import pytest

from domain.faq.entities import FAQResponse
from infrastructure.llm.graphs.faq.faq_node import faq_node


class TestFAQNode:
    """Tests for FAQ LangGraph node"""

    @pytest.fixture
    def mock_faq_response(self):
        """Mock FAQ service response"""
        return FAQResponse(
            answer="Привет! The Secret House предлагает зеленую и белую спальни с уникальным дизайном.",
            tokens_used=120,
            response_time=1.5,
            needs_human_help=False,
            suggested_actions=["booking"],
        )

    @pytest.mark.asyncio
    async def test_faq_node_basic_question(self, mock_faq_response):
        """Test FAQ node with basic question processing"""
        initial_state = {"text": "какие комнаты есть в доме?", "user_id": 12345}

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.return_value = mock_faq_response
            mock_service_class.return_value = mock_service

            result = await faq_node(initial_state)

            assert "reply" in result
            assert result["reply"] == mock_faq_response.answer
            assert result["intent"] == "faq"
            assert "faq_data" in result
            assert "faq_context" in result

            # Check that service was called
            mock_service.get_faq_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_faq_node_with_existing_context(self, mock_faq_response):
        """Test FAQ node with existing conversation context"""
        initial_state = {
            "text": "а сколько это стоит?",
            "user_id": 12345,
            "faq_context": {
                "conversation_history": [
                    {"role": "user", "content": "что есть в доме?"},
                    {"role": "assistant", "content": "Есть спальни и сауна"},
                ],
                "total_questions": 1,
            },
        }

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.return_value = mock_faq_response
            mock_service_class.return_value = mock_service

            result = await faq_node(initial_state)

            assert "reply" in result
            assert "faq_context" in result

            # Check that context was updated
            new_context = result["faq_context"]
            assert new_context["total_questions"] == 2
            assert len(new_context["conversation_history"]) == 4  # Previous 2 + new 2

    @pytest.mark.asyncio
    async def test_faq_node_human_escalation(self):
        """Test FAQ node when human help is needed"""
        escalation_response = FAQResponse(
            answer="Не уверен в этом вопросе.",
            tokens_used=50,
            response_time=0.8,
            needs_human_help=True,
            suggested_actions=[],
        )

        initial_state = {"text": "сложный вопрос", "user_id": 12345}

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.return_value = escalation_response
            mock_service_class.return_value = mock_service

            result = await faq_node(initial_state)

            assert "@the_secret_house" in result["reply"]

    @pytest.mark.asyncio
    async def test_faq_node_conversation_history_limit(self, mock_faq_response):
        """Test that conversation history is limited to last 12 messages"""
        long_history = []
        for i in range(20):  # More than 12 messages
            long_history.append({"role": "user", "content": f"Question {i}"})
            long_history.append({"role": "assistant", "content": f"Answer {i}"})

        initial_state = {
            "text": "новый вопрос",
            "user_id": 12345,
            "faq_context": {
                "conversation_history": long_history,
                "total_questions": 20,
            },
        }

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.return_value = mock_faq_response
            mock_service_class.return_value = mock_service

            result = await faq_node(initial_state)

            # Check that history is limited to 12 messages
            new_context = result["faq_context"]
            assert len(new_context["conversation_history"]) <= 12

    @pytest.mark.asyncio
    async def test_faq_node_error_handling(self):
        """Test FAQ node error handling when service fails"""
        initial_state = {"text": "тест вопрос", "user_id": 12345}

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.side_effect = Exception("Service error")
            mock_service_class.return_value = mock_service

            result = await faq_node(initial_state)

            assert "reply" in result
            assert result["intent"] == "faq"
            assert "error" in result
            assert "@the_secret_house" in result["reply"]

    @pytest.mark.asyncio
    async def test_faq_node_empty_text(self, mock_faq_response):
        """Test FAQ node with empty or missing text"""
        initial_state = {
            "user_id": 12345
            # No "text" field
        }

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.return_value = mock_faq_response
            mock_service_class.return_value = mock_service

            result = await faq_node(initial_state)

            # Should handle gracefully
            assert "reply" in result
            # FAQ node creates a new FAQContext() when none exists, so check that service was called
            mock_service.get_faq_response.assert_called_once()
            call_args = mock_service.get_faq_response.call_args
            assert call_args[0][0] == ""  # Empty text
            assert call_args[0][1] is not None  # FAQContext was created

    @pytest.mark.asyncio
    async def test_faq_node_logging_metrics(self, mock_faq_response):
        """Test that FAQ node logs performance metrics correctly"""
        initial_state = {"text": "какие удобства есть?", "user_id": 12345}

        with patch(
            "infrastructure.llm.graphs.faq.faq_node.FAQService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_faq_response.return_value = mock_faq_response
            mock_service_class.return_value = mock_service

            with patch("infrastructure.llm.graphs.faq.faq_node.logger") as mock_logger:
                await faq_node(initial_state)

                # Check that performance metrics were logged
                assert mock_logger.info.called
                log_calls = mock_logger.info.call_args_list

                # Should log both request processing and successful response
                assert len(log_calls) >= 2

                # Check that metrics are included in log
                final_log_call = log_calls[-1]
                extra_data = final_log_call[1]["extra"]
                assert "tokens_used" in extra_data
                assert "response_time" in extra_data
