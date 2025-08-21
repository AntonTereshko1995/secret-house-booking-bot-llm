from typing import Dict, Any
from application.services.booking_service import BookingService
from infrastructure.llm.graphs.common.graph_state import AppState
from infrastructure.llm.extractors.date_extractor import DateExtractor

svc = BookingService()
date_extractor = DateExtractor()

async def availability_node(s: AppState) -> Dict[str, Any]:
    # Пытаемся вытащить месяц из текста; fallback — текущий месяц
    month_start, month_end, matched_label = date_extractor.month_bounds_from_text(s.get("text", ""))

    # Сервисный вызов: получаем свободные даты/окна (сделай метод в своём сервисе)
    # Ожидается, что вернёт строку/список — отформатируй как тебе нужно
    data = await svc.availability_for_period(month_start, month_end)

    # Никакой бизнес-логики форматирования в графе — минимальный ответ
    return {"reply": f"{data}\n(запрос: {matched_label})"}
