"""
LLM-powered FAQ service for The Secret House
Обеспечивает интеллектуальные ответы на вопросы о доме используя ChatGPT/OpenAI
"""

import time

from langchain.schema import AIMessage, HumanMessage, SystemMessage

from core.logging import get_logger
from domain.faq.entities import FAQContext, FAQResponse
from infrastructure.llm.clients.openai_client import get_llm
from infrastructure.llm.graphs.faq.house_context import HouseContextBuilder

logger = get_logger(__name__)


class FAQService:
    """LLM-powered FAQ service with house context integration"""

    def __init__(self):
        self.llm = get_llm()  # Use existing OpenAI client
        self.house_context = HouseContextBuilder()
        self.system_prompt = self.house_context.build_system_prompt()

    async def get_faq_response(
        self, question: str, context: FAQContext | None = None
    ) -> FAQResponse:
        """Generate LLM-powered FAQ response with house context"""
        start_time = time.time()

        logger.info("Processing FAQ question", extra={"question": question[:100]})

        try:
            # CRITICAL: Build conversation history for context
            conversation_messages = []
            if context and context.conversation_history:
                # Keep last 6 messages for context (3 turns)
                for msg in context.conversation_history[-6:]:
                    if msg["role"] == "user":
                        conversation_messages.append(
                            HumanMessage(content=msg["content"])
                        )
                    elif msg["role"] == "assistant":
                        conversation_messages.append(AIMessage(content=msg["content"]))

            # PATTERN: Create message chain for LLM following booking_extractor pattern
            messages = [
                SystemMessage(content=self.system_prompt),
                *conversation_messages,
                HumanMessage(content=question),
            ]

            # CRITICAL: Call LLM with configured parameters
            logger.debug(
                "Calling LLM for FAQ response", extra={"messages_count": len(messages)}
            )
            response = await self.llm.ainvoke(messages)
            answer = response.content

            # PATTERN: Extract suggested actions from response
            suggested_actions = self._extract_bot_function_suggestions(answer)

            # PATTERN: Track performance metrics
            response_time = time.time() - start_time
            tokens_used = self._estimate_tokens_used(messages, response)

            logger.info(
                "LLM FAQ response generated successfully",
                extra={
                    "response_time": response_time,
                    "tokens_used": tokens_used,
                    "suggested_actions": suggested_actions,
                },
            )

            return FAQResponse(
                answer=answer,
                tokens_used=tokens_used,
                response_time=response_time,
                needs_human_help=self._should_escalate_to_human(answer),
                suggested_actions=suggested_actions,
            )

        except Exception:
            response_time = time.time() - start_time
            logger.exception(
                "Error generating LLM FAQ response", extra={"question": question[:100]}
            )

            # FALLBACK: Return error response
            return FAQResponse(
                answer="Извините, произошла ошибка при обработке вашего вопроса. Обратитесь к администратору @the_secret_house",
                tokens_used=0,
                response_time=response_time,
                needs_human_help=True,
                suggested_actions=[],
            )

    def _extract_bot_function_suggestions(self, response: str) -> list[str]:
        """Extract bot function suggestions from LLM response"""
        suggestions = []
        response_lower = response.lower()

        if "забронировать" in response_lower or "бронир" in response_lower:
            suggestions.append("booking")
        if "свободные даты" in response_lower or "доступн" in response_lower:
            suggestions.append("availability")
        if "сертификат" in response_lower or "подарок" in response_lower:
            suggestions.append("certificate")
        if (
            "цен" in response_lower
            or "стоимост" in response_lower
            or "тариф" in response_lower
        ):
            suggestions.append("pricing")

        return suggestions

    def _should_escalate_to_human(self, response: str) -> bool:
        """Determine if question should be escalated to human support"""
        escalation_phrases = [
            "не могу ответить",
            "обратитесь к администратору",
            "свяжитесь с нами",
            "не уверен",
            "не знаю",
            "обратись к",
            "@the_secret_house",
        ]
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in escalation_phrases)

    def _estimate_tokens_used(self, messages: list, response) -> int:
        """Estimate tokens used in the request (rough approximation)"""
        try:
            # Rough estimation: ~1 token per 4 characters for Russian text
            total_chars = sum(
                len(msg.content) for msg in messages if hasattr(msg, "content")
            )
            total_chars += len(response.content) if hasattr(response, "content") else 0
            return total_chars // 3  # Conservative estimate for Russian text
        except Exception:
            return 0
