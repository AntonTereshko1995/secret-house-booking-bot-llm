from typing import Any, Dict
from infrastructure.llm.extractors.booking_extractor import BookingExtractor
from infrastructure.llm.graphs.common.graph_state import AppState

extractor = BookingExtractor()

async def parse_input(state):
    text = state.get("text","")
    fields = await extractor.aextract(text)
    ctx = {**state.get("ctx", {}), **fields}
    missing = [k for k in ("START_DATE","START_TIME","TARIFF") if not ctx.get(k)]
    return {"ctx": ctx, "missing": missing}

async def booking_exit_node(s: AppState) -> Dict[str, Any]:
    # Сбрасываем active_subgraph ТОЛЬКО если сабграф пометил завершение
    if s.get("done"):
        # копию словаря безопаснее возвращать, чем мутировать вход
        new_state = dict(s)
        new_state.pop("active_subgraph", None)
        return new_state
    return {}