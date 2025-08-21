from typing import Dict, Any
from application.services.booking_service import BookingService
from infrastructure.llm.graphs.common.graph_state import AppState
from infrastructure.llm.extractors.date_extractor import DateExtractor

svc = BookingService()
date_extractor = DateExtractor()

async def availability_node(s: AppState) -> Dict[str, Any]:
    # Try to extract month from text; fallback - current month
    month_start, month_end, matched_label = date_extractor.month_bounds_from_text(s.get("text", ""))

    # Service call: get available dates/windows (implement method in your service)
    # Expected to return string/list - format as needed
    data = await svc.availability_for_period(month_start, month_end)

    # No business logic formatting in graph - minimal response
    return {"reply": f"{data}\n(request: {matched_label})"}
