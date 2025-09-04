"""
Unit tests for FAQ domain entities
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from domain.faq.entities import (
    FAQContext,
    FAQPrompt,
    FAQResponse,
    FAQSession,
    HouseInformation,
)


class TestFAQEntities:
    """Tests for FAQ domain entities"""

    def test_faq_prompt_creation(self):
        """Test FAQPrompt entity creation with defaults"""
        prompt = FAQPrompt(system_prompt="Test prompt")

        assert prompt.system_prompt == "Test prompt"
        assert prompt.temperature == 0.7
        assert prompt.max_tokens == 500
        assert prompt.language == "russian"

    def test_faq_prompt_validation(self):
        """Test FAQPrompt validation constraints"""
        # Valid temperature range
        prompt = FAQPrompt(system_prompt="Test", temperature=1.5)
        assert prompt.temperature == 1.5

        # Invalid temperature - too high
        with pytest.raises(ValidationError):
            FAQPrompt(system_prompt="Test", temperature=2.5)

        # Invalid temperature - negative
        with pytest.raises(ValidationError):
            FAQPrompt(system_prompt="Test", temperature=-0.1)

        # Invalid max_tokens - zero
        with pytest.raises(ValidationError):
            FAQPrompt(system_prompt="Test", max_tokens=0)

    def test_faq_response_creation(self):
        """Test FAQResponse entity creation"""
        response = FAQResponse(
            answer="Тест ответ",
            tokens_used=150,
            response_time=1.2,
            suggested_actions=["booking", "pricing"],
        )

        assert response.answer == "Тест ответ"
        assert response.tokens_used == 150
        assert response.response_time == 1.2
        assert response.needs_human_help is False
        assert response.suggested_actions == ["booking", "pricing"]

    def test_faq_response_validation(self):
        """Test FAQResponse validation constraints"""
        # Invalid tokens_used - negative
        with pytest.raises(ValidationError):
            FAQResponse(answer="Test", tokens_used=-1)

        # Invalid response_time - negative
        with pytest.raises(ValidationError):
            FAQResponse(answer="Test", response_time=-0.1)

    def test_faq_context_creation(self):
        """Test FAQContext entity creation with conversation history"""
        context = FAQContext(
            conversation_history=[
                {"role": "user", "content": "Привет"},
                {"role": "assistant", "content": "Здравствуйте!"},
            ],
            total_questions=1,
        )

        assert len(context.conversation_history) == 2
        assert context.conversation_history[0]["role"] == "user"
        assert context.conversation_history[1]["role"] == "assistant"
        assert context.total_questions == 1
        assert isinstance(context.session_start, datetime)

    def test_faq_context_validation(self):
        """Test FAQContext validation constraints"""
        # Invalid total_questions - negative
        with pytest.raises(ValidationError):
            FAQContext(total_questions=-1)

    def test_house_information_creation(self):
        """Test HouseInformation entity creation"""
        house_info = HouseInformation(
            location="Test location",
            rooms={"bedroom": "Описание спальни"},
            amenities={"sauna": "Сауна с подогревом"},
            tariffs=[{"name": "Стандарт", "price": 500}],
            policies={"payment": "Предоплата 80 руб"},
            contact_info={"admin": "@test_admin"},
        )

        assert house_info.location == "Test location"
        assert house_info.rooms["bedroom"] == "Описание спальни"
        assert house_info.amenities["sauna"] == "Сауна с подогревом"
        assert len(house_info.tariffs) == 1
        assert house_info.tariffs[0]["name"] == "Стандарт"
        assert house_info.policies["payment"] == "Предоплата 80 руб"
        assert house_info.contact_info["admin"] == "@test_admin"

    def test_faq_session_creation(self):
        """Test FAQSession entity creation and tracking"""
        session = FAQSession(
            session_id="test-session-123",
            user_id=12345,
            total_questions=5,
            total_tokens_used=1200,
            escalated_to_human=True,
        )

        assert session.session_id == "test-session-123"
        assert session.user_id == 12345
        assert session.total_questions == 5
        assert session.total_tokens_used == 1200
        assert session.escalated_to_human is True
        assert session.end_time is None
        assert isinstance(session.start_time, datetime)

    def test_faq_session_validation(self):
        """Test FAQSession validation constraints"""
        # Invalid total_questions - negative
        with pytest.raises(ValidationError):
            FAQSession(session_id="test", user_id=1, total_questions=-1)

        # Invalid total_tokens_used - negative
        with pytest.raises(ValidationError):
            FAQSession(session_id="test", user_id=1, total_tokens_used=-1)

        # Invalid user_satisfaction - out of range
        with pytest.raises(ValidationError):
            FAQSession(session_id="test", user_id=1, user_satisfaction=6)

        with pytest.raises(ValidationError):
            FAQSession(session_id="test", user_id=1, user_satisfaction=0)

    def test_unicode_handling(self):
        """Test proper Unicode handling for Russian text"""
        response = FAQResponse(
            answer="🏠 The Secret House — это уникальное место с невероятными возможностями! 🔥",
            tokens_used=100,
        )

        assert "🏠" in response.answer
        assert "🔥" in response.answer
        assert "уникальное" in response.answer
