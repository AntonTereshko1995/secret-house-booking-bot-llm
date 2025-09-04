"""
Unit tests for LLM-powered FAQService
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from application.services.faq_service import FAQService
from domain.faq.entities import FAQContext, FAQResponse


class TestFAQService:
    """Tests for LLM-powered FAQService"""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response"""
        mock_response = MagicMock()
        mock_response.content = "Привет! The Secret House предлагает уникальные комнаты: зеленую и белую спальни с современным дизайном. Для бронирования перейдите в пункт меню 'Забронировать'!"
        return mock_response

    @pytest.fixture
    def faq_service(self):
        """Create FAQService instance with mocked LLM"""
        with patch("application.services.faq_service.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            service = FAQService()
            service.llm = mock_llm
            return service

    @pytest.mark.asyncio
    async def test_get_faq_response_basic_question(
        self, faq_service, mock_llm_response
    ):
        """Test LLM-powered FAQ response for basic question"""
        faq_service.llm.ainvoke = AsyncMock(return_value=mock_llm_response)
        question = "какие комнаты есть в доме?"

        response = await faq_service.get_faq_response(question)

        assert isinstance(response, FAQResponse)
        assert isinstance(response.answer, str)
        assert len(response.answer) > 0
        assert response.tokens_used >= 0
        assert response.response_time >= 0
        assert isinstance(response.suggested_actions, list)

        # Check that LLM was called
        faq_service.llm.ainvoke.assert_called_once()

        # Check that system prompt includes house information
        call_args = faq_service.llm.ainvoke.call_args[0][0]
        system_message = call_args[0]
        assert "The Secret House" in system_message.content
        assert "зеленая спальня" in system_message.content.lower()

    @pytest.mark.asyncio
    async def test_get_faq_response_with_context(self, faq_service, mock_llm_response):
        """Test FAQ response with conversation context"""
        faq_service.llm.ainvoke = AsyncMock(return_value=mock_llm_response)

        context = FAQContext(
            conversation_history=[
                {"role": "user", "content": "что есть в доме?"},
                {"role": "assistant", "content": "Есть спальни, кухня, сауна"},
            ]
        )
        question = "а сколько это стоит?"

        response = await faq_service.get_faq_response(question, context)

        assert isinstance(response, FAQResponse)
        assert response.tokens_used >= 0

        # Check that conversation history was included
        call_args = faq_service.llm.ainvoke.call_args[0][0]
        assert len(call_args) > 2  # System + history + current question

    @pytest.mark.asyncio
    async def test_get_faq_response_booking_suggestion(self, faq_service):
        """Test that booking suggestions are extracted correctly"""
        mock_response = MagicMock()
        mock_response.content = (
            "Для бронирования дома перейдите в пункт меню 'Забронировать'"
        )
        faq_service.llm.ainvoke = AsyncMock(return_value=mock_response)

        question = "как забронировать?"
        response = await faq_service.get_faq_response(question)

        assert "booking" in response.suggested_actions

    @pytest.mark.asyncio
    async def test_get_faq_response_pricing_suggestion(self, faq_service):
        """Test that pricing suggestions are extracted correctly"""
        mock_response = MagicMock()
        mock_response.content = (
            "Стоимость аренды зависит от тарифа. Цена начинается от 180 BYN."
        )
        faq_service.llm.ainvoke = AsyncMock(return_value=mock_response)

        question = "сколько стоит?"
        response = await faq_service.get_faq_response(question)

        assert "pricing" in response.suggested_actions

    @pytest.mark.asyncio
    async def test_get_faq_response_escalation_detection(self, faq_service):
        """Test escalation to human support detection"""
        mock_response = MagicMock()
        mock_response.content = "Не могу ответить на этот вопрос. Обратитесь к администратору @the_secret_house"
        faq_service.llm.ainvoke = AsyncMock(return_value=mock_response)

        question = "сложный вопрос"
        response = await faq_service.get_faq_response(question)

        assert response.needs_human_help is True

    @pytest.mark.asyncio
    async def test_get_faq_response_error_handling(self, faq_service):
        """Test error handling when LLM call fails"""
        faq_service.llm.ainvoke = AsyncMock(side_effect=Exception("LLM API error"))

        question = "тест вопрос"
        response = await faq_service.get_faq_response(question)

        assert isinstance(response, FAQResponse)
        assert response.needs_human_help is True
        assert "@the_secret_house" in response.answer
        assert response.tokens_used == 0
        assert response.response_time > 0

    def test_extract_bot_function_suggestions(self, faq_service):
        """Test extraction of bot function suggestions from responses"""
        # Test booking suggestion
        response_text = "Для бронирования перейдите в меню"
        suggestions = faq_service._extract_bot_function_suggestions(response_text)
        assert "booking" in suggestions

        # Test availability suggestion
        response_text = "Проверьте свободные даты в календаре"
        suggestions = faq_service._extract_bot_function_suggestions(response_text)
        assert "availability" in suggestions

        # Test certificate suggestion
        response_text = "Можете приобрести подарочный сертификат"
        suggestions = faq_service._extract_bot_function_suggestions(response_text)
        assert "certificate" in suggestions

        # Test pricing suggestion
        response_text = "Узнайте о ценах и тарифах"
        suggestions = faq_service._extract_bot_function_suggestions(response_text)
        assert "pricing" in suggestions

    def test_should_escalate_to_human(self, faq_service):
        """Test human escalation detection logic"""
        # Should escalate
        escalation_responses = [
            "Не могу ответить на этот вопрос",
            "Обратитесь к администратору",
            "Не уверен в этом",
            "Свяжитесь с @the_secret_house",
        ]

        for response_text in escalation_responses:
            assert faq_service._should_escalate_to_human(response_text) is True

        # Should not escalate
        normal_response = "Дом находится в 12 км от Минска"
        assert faq_service._should_escalate_to_human(normal_response) is False

    def test_estimate_tokens_used(self, faq_service):
        """Test token usage estimation"""
        from langchain.schema import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content="System prompt content"),
            HumanMessage(content="User question"),
        ]

        mock_response = MagicMock()
        mock_response.content = "Response content"

        tokens = faq_service._estimate_tokens_used(messages, mock_response)
        assert tokens > 0
        assert isinstance(tokens, int)

    @pytest.mark.asyncio
    async def test_russian_unicode_handling(self, faq_service, mock_llm_response):
        """Test proper handling of Russian Unicode text"""
        mock_llm_response.content = "🏠 Уникальное место с современными удобствами! 🔥"
        faq_service.llm.ainvoke = AsyncMock(return_value=mock_llm_response)

        question = "что такое секретная комната?"
        response = await faq_service.get_faq_response(question)

        assert "🏠" in response.answer
        assert "🔥" in response.answer
        assert "Уникальное" in response.answer
