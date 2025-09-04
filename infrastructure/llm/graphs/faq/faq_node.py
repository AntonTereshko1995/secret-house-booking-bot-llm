"""
LLM-powered FAQ node for LangGraph integration
Обрабатывает FAQ запросы используя ChatGPT и контекст о доме
"""

from typing import Any

from application.services.faq_service import FAQService
from core.logging import get_logger
from domain.faq.entities import FAQContext
from infrastructure.llm.graphs.common.graph_state import AppState

logger = get_logger(__name__)


async def faq_node(state: AppState) -> dict[str, Any]:
    """
    Обрабатывает FAQ запросы с использованием LLM-генерированных ответов
    Интегрируется с существующей архитектурой LangGraph
    """
    user_text = state.get("text", "")
    user_id = state.get("user_id", 0)

    logger.info(
        "Processing LLM FAQ request",
        extra={"user_text": user_text[:100], "user_id": user_id},
    )

    try:
        # PATTERN: Extract and build FAQ context from conversation history
        faq_context_data = state.get("faq_context")
        if faq_context_data:
            faq_context = FAQContext(**faq_context_data)
        else:
            faq_context = FAQContext()

        logger.debug(
            "FAQ context loaded",
            extra={
                "conversation_history_length": len(faq_context.conversation_history),
                "total_questions": faq_context.total_questions,
            },
        )

        # CRITICAL: Generate LLM-powered response
        faq_service = FAQService()
        faq_response = await faq_service.get_faq_response(user_text, faq_context)

        # PATTERN: Use LLM-generated response directly
        reply = faq_response.answer

        # CRITICAL: Add human escalation if needed
        if faq_response.needs_human_help:
            if "@the_secret_house" not in reply:
                reply += "\\n\\n🙋‍♂️ Для получения детальной консультации обращайтесь к администратору @the_secret_house"

        # PATTERN: Update conversation context for LLM continuity
        updated_history = faq_context.conversation_history.copy()
        updated_history.append({"role": "user", "content": user_text})
        updated_history.append({"role": "assistant", "content": reply})

        # Keep last 12 messages for context (6 conversation turns)
        new_faq_context = FAQContext(
            conversation_history=updated_history[-12:],
            user_preferences=faq_context.user_preferences,
            session_start=faq_context.session_start,
            total_questions=faq_context.total_questions + 1,
        )

        # PATTERN: Log LLM performance metrics
        logger.info(
            "LLM FAQ response generated successfully",
            extra={
                "user_id": user_id,
                "tokens_used": faq_response.tokens_used,
                "response_time": faq_response.response_time,
                "needs_human_help": faq_response.needs_human_help,
                "suggested_actions": faq_response.suggested_actions,
                "conversation_turn": new_faq_context.total_questions,
            },
        )

        return {
            "reply": reply,
            "faq_data": faq_response.model_dump(),
            "faq_context": new_faq_context.model_dump(),
            "intent": "faq",  # Maintain intent
        }

    except Exception as e:
        logger.exception(
            "Error in faq_node",
            extra={"user_text": user_text[:100], "user_id": user_id},
        )
        return {
            "reply": "Произошла ошибка при обработке вашего вопроса. Обратитесь к администратору @the_secret_house для получения помощи.",
            "intent": "faq",
            "error": str(e),
        }
