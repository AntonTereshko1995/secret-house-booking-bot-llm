"""
Узел для обработки запросов ценообразования
"""

from typing import Any

from application.services.pricing_service import PricingService
from core.logging import get_logger
from infrastructure.llm.extractors.pricing_extractor import PricingExtractor
from infrastructure.llm.graphs.common.graph_state import AppState

logger = get_logger(__name__)
pricing_service = PricingService()
pricing_extractor = PricingExtractor()


async def pricing_node(s: AppState) -> dict[str, Any]:
    """
    Обрабатывает запросы на получение информации о ценах.
    Использует PricingExtractor для извлечения требований из текста
    и PricingService для расчета стоимости.
    """
    user_text = s.get("text", "")
    logger.info("Processing pricing request", extra={"user_text": user_text})

    try:
        # Проверяем, является ли это запросом на сравнение тарифов
        if pricing_extractor.extract_comparison_request(user_text):
            # Возвращаем общий обзор всех тарифов
            reply = await pricing_service.get_tariffs_summary()
            reply += "\n\n💬 Для расчета конкретной стоимости укажите желаемый тариф и количество дней."

            return {
                "reply": reply,
                "intent": "price",
                "pricing_data": {"type": "comparison", "all_tariffs": True},
            }

        # Извлекаем требования к ценообразованию
        pricing_request = await pricing_extractor.extract_pricing_requirements(user_text)

        logger.debug(
            "Extracted pricing requirements",
            extra={
                "user_text": user_text,
                "pricing_request": pricing_request.dict(exclude_none=True),
            },
        )

        # Если не извлекли конкретный тариф, но есть признаки ценового запроса
        if not pricing_request.tariff and pricing_extractor.is_pricing_query(user_text):
            # Показываем общую информацию о тарифах
            reply = await pricing_service.get_tariffs_summary()
            reply += "\n\n💡 Для точного расчета стоимости укажите:"
            reply += "\n• Желаемый тариф"
            reply += "\n• Количество дней"
            reply += "\n• Дополнительные услуги (при необходимости)"
            reply += "\n\nНапример: *'Сколько стоит суточный тариф на 3 дня с сауной?'*"

            return {
                "reply": reply,
                "intent": "price",
                "pricing_data": {"type": "general_inquiry"},
            }

        # Рассчитываем стоимость
        pricing_response = await pricing_service.calculate_pricing(pricing_request)

        # Форматируем ответ
        reply = pricing_response.formatted_message
        if pricing_response.booking_suggestion:
            reply += f"\n\n{pricing_response.booking_suggestion}"

        return {
            "reply": reply,
            "intent": "price",
            "pricing_data": {
                "breakdown": pricing_response.breakdown.dict(),
                "request": pricing_request.dict(exclude_none=True),
                "valid_until": pricing_response.valid_until.isoformat(),
            },
        }

    except ValueError as ve:
        # Ошибки валидации (например, неизвестный тариф)
        logger.warning("Validation error in pricing_node", extra={
            "user_text": user_text,
            "error": str(ve)
        })

        reply = "⚠️ Не удалось найти указанный тариф.\n\n"
        reply += await pricing_service.get_tariffs_summary()
        reply += "\n💬 Пожалуйста, выберите один из доступных тарифов."

        return {
            "reply": reply,
            "intent": "price",
            "error": "unknown_tariff",
        }

    except Exception as e:
        logger.exception("Error in pricing_node", extra={"user_text": user_text})

        reply = "😔 Произошла ошибка при расчете стоимости."
        reply += "\n\nПопробуйте переформулировать запрос или обратитесь к администратору."
        reply += "\n\n💡 Пример корректного запроса:"
        reply += "\n*'Сколько стоит суточный тариф для двоих на 2 дня?'*"

        return {
            "reply": reply,
            "intent": "price",
            "error": str(e),
        }
