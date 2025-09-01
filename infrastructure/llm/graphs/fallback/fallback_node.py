from typing import Dict, Any

from infrastructure.llm.graphs.common.graph_state import AppState


async def fallback_node(s: AppState) -> Dict[str, Any]:
    return {
        "reply": "Я понимаю запросы: бронирование, свободные даты, изменение брони, FAQ. Попробуй сформулировать иначе."
    }
