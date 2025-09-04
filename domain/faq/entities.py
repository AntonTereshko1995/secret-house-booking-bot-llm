"""
FAQ доменные сущности для LLM-powered системы FAQ
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FAQPrompt(BaseModel):
    """LLM prompt configuration for FAQ responses"""

    system_prompt: str  # System context with house information
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0
    )  # Creativity level for responses
    max_tokens: int = Field(default=500, gt=0)  # Response length limit
    language: str = Field(default="russian")  # Primary response language

    class Config:
        from_attributes = True


class FAQResponse(BaseModel):
    """LLM-generated FAQ response"""

    answer: str  # Generated response from LLM
    tokens_used: int = Field(default=0, ge=0)  # Token consumption tracking
    response_time: float = Field(default=0.0, ge=0.0)  # Response generation time
    needs_human_help: bool = Field(default=False)  # Escalation flag
    suggested_actions: list[str] = Field(
        default_factory=list
    )  # Bot function suggestions

    class Config:
        from_attributes = True


class FAQContext(BaseModel):
    """FAQ conversation context for LLM continuity"""

    conversation_history: list[dict[str, str]] = Field(
        default_factory=list
    )  # [{"role": "user/assistant", "content": "..."}]
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    session_start: datetime = Field(default_factory=datetime.now)
    total_questions: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True


class HouseInformation(BaseModel):
    """Structured house information for LLM context"""

    location: str
    rooms: dict[str, str]  # Room name -> description
    amenities: dict[str, str]  # Amenity -> details
    tariffs: list[dict[str, Any]]  # Pricing information
    policies: dict[str, str]  # Rules and policies
    contact_info: dict[str, str]  # Contact details

    class Config:
        from_attributes = True


class FAQSession(BaseModel):
    """FAQ session tracking for analytics"""

    session_id: str
    user_id: int
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = None
    total_questions: int = Field(default=0, ge=0)
    total_tokens_used: int = Field(default=0, ge=0)
    escalated_to_human: bool = Field(default=False)
    user_satisfaction: int | None = Field(default=None, ge=1, le=5)  # 1-5 rating

    class Config:
        from_attributes = True
