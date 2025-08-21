import re
from typing import Dict, Any
from infrastructure.llm.graphs.common.graph_state import AppState

# простой роутер; легко заменить на LLM-классификатор
async def router_node(s: AppState) -> Dict[str, Any]:
    t = (s.get("text") or "").lower()

    # Если уже внутри сабграфа — продолжить его
    if s.get("active_subgraph") == "booking":
        return {"intent": "booking"}

    if re.search(r"(заброниров|бронь|арендовать)", t):
        return {"intent": "booking", "active_subgraph": "booking"}
    if re.search(r"(свободн|дат[ыа]|календар)", t):
        return {"intent": "availability"}
    if re.search(r"(измен|перенос)", t):
        return {"intent": "change"}
    if re.search(r"(правил|что такое|faq)", t):
        return {"intent": "faq"}
    return {"intent": "unknown"}