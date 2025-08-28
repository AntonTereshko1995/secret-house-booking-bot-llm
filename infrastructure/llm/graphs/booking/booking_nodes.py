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
    print(f"DEBUG booking_exit_node: done={s.get('done')}, await_input={s.get('await_input')}")
    # Always preserve the state, let the main graph handle routing
    return s