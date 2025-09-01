from typing import Any

from application.services.availability_service import AvailabilityService
from application.services.booking_service import BookingService
from core.logging import get_logger
from infrastructure.llm.extractors.date_extractor import DateExtractor
from infrastructure.llm.graphs.common.graph_state import AppState

logger = get_logger(__name__)
svc = BookingService()
availability_service = AvailabilityService()
date_extractor = DateExtractor()


async def availability_node(s: AppState) -> dict[str, Any]:
    """
    Обрабатывает запросы на проверку доступности дат.
    Использует улучшенный DateExtractor для извлечения дат из текста.
    """
    user_text = s.get("text", "")
    logger.info("Processing availability request", extra={"user_text": user_text})

    try:
        # Используем улучшенный метод для извлечения дат
        start_date, end_date, matched_label = date_extractor.extract_dates_from_text(
            user_text
        )

        logger.debug(
            "Extracted dates",
            extra={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "matched_label": matched_label,
            },
        )

        # Получаем информацию о доступности
        availability_data = await availability_service.get_availability_for_period(
            start_date, end_date
        )

        # Формируем пользователю понятный ответ на русском языке
        reply = _format_availability_response(availability_data, matched_label)

        return {
            "reply": reply,
            "availability_data": availability_data,
            "dates_extracted": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "matched_text": matched_label,
            },
        }

    except Exception as e:
        logger.exception("Error in availability_node", extra={"user_text": user_text})
        return {
            "reply": "Произошла ошибка при проверке доступности. Попробуйте переформулировать запрос или попробуйте позже.",
            "error": str(e),
        }


def _format_availability_response(availability_data, matched_label: str) -> str:
    """
    Форматирует ответ о доступности в удобочитаемом виде на русском языке
    """
    available_count = availability_data.total_available_days
    total_days = len(availability_data.slots)

    if available_count == 0:
        reply = f"К сожалению, на {matched_label} нет свободных дней."
        reply += "\n\nПопробуйте выбрать другие даты или свяжитесь с нами для уточнения возможностей."
    elif available_count == total_days:
        reply = f"Отлично! Все {total_days} дней в {matched_label} свободны для бронирования."
        reply += (
            "\n\nХотите забронировать? Напишите даты и время, которые вас интересуют."
        )
    else:
        reply = f"В {matched_label} свободно {available_count} из {total_days} дней."

        # Добавляем информацию о конкретных свободных датах
        available_dates = []
        for slot in availability_data.slots:
            if slot.is_available:
                available_dates.append(slot.date.strftime("%d.%m"))

        if (
            available_dates and len(available_dates) <= 10
        ):  # Показываем даты, если их не слишком много
            dates_str = ", ".join(available_dates)
            reply += f"\n\nСвободные даты: {dates_str}"

        reply += "\n\nХотите забронировать одну из свободных дат? Напишите конкретную дату и время."

    return reply
