import re
from typing import Any

from infrastructure.llm.graphs.common.graph_state import AppState


# simple router; easy to replace with LLM classifier
async def router_node(s: AppState) -> dict[str, Any]:
    t = (s.get("text") or "").lower()

    # If already inside subgraph and waiting for input - continue it
    if (
        s.get("active_subgraph") == "booking"
        and s.get("await_input")
        and not s.get("done")
    ):
        return {"intent": "booking", "active_subgraph": "booking"}

    # If we have booking context but no active subgraph, continue booking (unless done)
    if s.get("context") and not s.get("active_subgraph") and not s.get("done"):
        return {"intent": "booking", "active_subgraph": "booking"}

    # If done and user confirms - continue booking for finalization
    if s.get("done") and "подтверждаю" in t:
        return {"intent": "booking", "active_subgraph": "booking"}

    # If we have FAQ context, continue FAQ conversation for follow-up questions
    if s.get("faq_context"):
        return {"intent": "faq"}

    if re.search(r"(заброниров|бронь|арендовать)", t):
        return {"intent": "booking", "active_subgraph": "booking"}
    if re.search(
        r"(цен[аыу]|стоимост|сколько.*стоит|прайс|тариф|расценк|price|cost|how much)", t
    ):
        return {"intent": "price"}
    if re.search(r"(свободн|дат[ыа]|календар)", t):
        return {"intent": "availability"}
    if re.search(r"(измен|перенос)", t):
        return {"intent": "change"}
    # Enhanced FAQ intent detection with comprehensive Russian patterns
    if re.search(r"(правил|что такое|faq)", t):
        return {"intent": "faq"}
    # Question words and patterns
    if re.search(
        r"(что.*есть|что.*включ|что.*входит|какие.*услуги|какие.*удобства|какие.*комнат)", t
    ):
        return {"intent": "faq"}
    if re.search(r"(как.*работает|как.*добраться|как.*заселиться|как.*оплатить)", t):
        return {"intent": "faq"}
    if re.search(r"(где.*находится|где.*дом|где.*расположен|где.*парков)", t):
        return {"intent": "faq"}
    if re.search(r"(можно ли|нельзя ли|разрешено ли|есть ли)", t):
        return {"intent": "faq"}
    if re.search(r"(расскажи|опиши|покажи|информац|подробнее)", t):
        return {"intent": "faq"}
    if re.search(r"(условия|требования|политика|ограничения)", t):
        return {"intent": "faq"}
    # Equipment and room-specific questions
    if re.search(r"(оборудование|мебель|аксессуар|техника)", t):
        return {"intent": "faq"}
    if re.search(r"(секретн.*комнат|зелен.*спальн|бел.*спальн|сауна|кухн|гостин)", t):
        return {"intent": "faq"}
    # English patterns
    if re.search(r"(what.*is|what.*include|how.*work|where.*located|can.*i|may.*i)", t):
        return {"intent": "faq"}
    return {"intent": "unknown"}
