from typing import Any

from infrastructure.llm.graphs.common.graph_state import AppState


async def fallback_node(s: AppState) -> dict[str, Any]:
    return {
        "reply": "Я понимаю запросы: бронирование, свободные даты, изменение брони, FAQ. Попробуй сформулировать иначе."
    }
