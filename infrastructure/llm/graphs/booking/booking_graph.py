
from langgraph.graph import END, START, StateGraph

from core.utils.datetime_helper import (
    extract_date_from_natural_language,
    is_date,
    is_time,
    norm_date,
    norm_time,
)
from core.utils.string_helper import parse_yes_no
from infrastructure.llm.extractors import booking_extractor
from infrastructure.llm.graphs.common.graph_state import BookingState

REQUIRED = [
    "TARIFF",
    "START_DATE",
    "START_TIME",
    "FINISH_DATE",
    "FINISH_TIME",
    "FIRST_BEDROOM",
    "SECOND_BEDROOM",
    "SAUNA",
    "PHOTOSHOOT",
    "SECRET_ROOM",
    "NUMBER_GUESTS",
    "CONTACT",
    "COMMENT",
]
QUESTIONS = {
    "TARIFF": "Укажи тариф: `12 часов`, `Суточно для пар`, `Суточно от 3-ех человек`, `Инконито 12 часов`, `Инкогнито на сутки`, `Рабочий`.",
    "START_DATE": "Дата заезда? `ДД.ММ` или `ДД.ММ.ГГГГ`.",
    "START_TIME": "Время заезда? `HH:MM`.",
    "FINISH_DATE": "Дата выезда? `ДД.ММ` или `ДД.ММ.ГГГГ`.",
    "FINISH_TIME": "Время выезда? `HH:MM`.",
    "FIRST_BEDROOM": "Нужна первая спальня? (`да`/`нет`)",
    "SECOND_BEDROOM": "Нужна вторая спальня? (`да`/`нет`)",
    "SAUNA": "Добавить сауну? (`да`/`нет`)",
    "PHOTOSHOOT": "Нужна фотосъёмка? (`да`/`нет`)",
    "SECRET_ROOM": "Нужна секретная комната? (`да`/`нет`)",
    "NUMBER_GUESTS": "Сколько гостей будет? Укажи числом.",
    "CONTACT": "Контакт для связи: `@username` или телефон с `+`.",
    "COMMENT": "Комментарий к брони (или напиши `нет`).",
}

booking_extractor = booking_extractor.BookingExtractor()


def _first_missing(ctx: dict) -> str | None:
    print(f"DEBUG _first_missing: ctx keys = {list(ctx.keys())}")
    for f in REQUIRED:
        if f not in ctx or ctx[f] in (None, ""):
            print(f"DEBUG: missing field '{f}'")
            return f
    print("DEBUG: no missing fields")
    return None


async def ask_or_fill(state: BookingState) -> BookingState:
    ctx = dict(state.get("context", {}))
    text = (state.get("text") or "").strip()

    # Process incoming text if present
    if text:
        # 1) Try LLM parser first
        try:
            parsed = await booking_extractor.aextract(text)
            if parsed:
                ctx.update(parsed)
        except Exception:
            pass

        # 2) Manual parsing for specific fields
        miss = _first_missing(ctx)
        if miss:
            print(f"DEBUG: processing field {miss} with text '{text}'")
            # Process the field and continue without setting await_input
            if miss == "TARIFF":
                low = text.lower()
                print(f"DEBUG TARIFF processing: text='{text}', low='{low}'")
                if "12" in low and "инкогнито" not in low:
                    print("DEBUG: setting TARIFF to '12 часов'")
                    ctx[miss] = "12 часов"
                elif "инкогнито" in low and "12" in low:
                    print("DEBUG: setting TARIFF to 'Инконито 12 часов'")
                    ctx[miss] = "Инконито 12 часов"
                elif "инкогнито" in low and (
                    "сут" in low or "24" in low or "день" in low
                ):
                    print("DEBUG: setting TARIFF to 'Инкогнито на сутки'")
                    ctx[miss] = "Инкогнито на сутки"
                elif "суточно" in low and ("пар" in low or "два" in low or "2" in low):
                    print("DEBUG: setting TARIFF to 'Суточно для пар'")
                    ctx[miss] = "Суточно для пар"
                elif "суточно" in low and (
                    "3" in low or "трех" in low or "трех" in low or "от 3" in low
                ):
                    print("DEBUG: setting TARIFF to 'Суточно от 3-ех человек'")
                    ctx[miss] = "Суточно от 3-ех человек"
                elif "рабочий" in low or "работа" in low:
                    print("DEBUG: setting TARIFF to 'Рабочий'")
                    ctx[miss] = "Рабочий"
                elif "сут" in low or "24" in low or "день" in low:
                    print("DEBUG: setting TARIFF to 'Суточно для пар' (default)")
                    ctx[miss] = "Суточно для пар"
                else:
                    print("DEBUG: no TARIFF match found")
            elif miss in {
                "FIRST_BEDROOM",
                "SECOND_BEDROOM",
                "SAUNA",
                "PHOTOSHOOT",
                "SECRET_ROOM",
            }:
                v = parse_yes_no(text)
                if v is not None:
                    ctx[miss] = v
            elif miss in {"START_DATE", "FINISH_DATE"}:
                # Try exact date format first
                if is_date(text):
                    ctx[miss] = norm_date(text)
                else:
                    # Try to extract date from natural language
                    extracted_date = extract_date_from_natural_language(text)
                    if extracted_date:
                        ctx[miss] = extracted_date
                        print(
                            f"DEBUG: extracted date '{extracted_date}' from natural language"
                        )
            elif miss in {"START_TIME", "FINISH_TIME"} and is_time(text):
                ctx[miss] = norm_time(text)
            elif miss == "NUMBER_GUESTS" and text.isdigit() and int(text) > 0:
                ctx[miss] = int(text)
            elif miss == "CONTACT" and (text.startswith("@") or text.startswith("+")):
                ctx[miss] = text
            elif miss == "COMMENT":
                ctx[miss] = None if text.lower() in {"нет", "no", "-"} else text

    # Check what's missing and ask next question
    miss = _first_missing(ctx)
    if miss:
        print(f"DEBUG ask_or_fill: asking for {miss}")
        print(f"DEBUG: current context keys: {list(ctx.keys())}")
        return {
            "context": ctx,
            "text": "",  # Always clear text after processing
            "reply": QUESTIONS[miss],
            "done": False,
            "await_input": False,  # Don't exit subgraph, continue processing
            "last_asked": miss,
            "active_subgraph": "booking",
        }

    # All fields collected - show summary and wait for "confirm"
    summary = (
        "📋 Резюме заявки:\n"
        f"Тариф: {ctx['TARIFF']}\n"
        f"Заезд: {ctx['START_DATE']} {ctx['START_TIME']}\n"
        f"Выезд: {ctx['FINISH_DATE']} {ctx['FINISH_TIME']}\n"
        f"1-я спальня: {'да' if ctx['FIRST_BEDROOM'] else 'нет'}\n"
        f"2-я спальня: {'да' if ctx['SECOND_BEDROOM'] else 'нет'}\n"
        f"Сауна: {'да' if ctx['SAUNA'] else 'нет'}\n"
        f"Фотосъёмка: {'да' if ctx['PHOTOSHOOT'] else 'нет'}\n"
        f"Секретная: {'да' if ctx['SECRET_ROOM'] else 'нет'}\n"
        f"Гостей: {ctx['NUMBER_GUESTS']}\n"
        f"Контакт: {ctx['CONTACT']}\n"
        f"Комментарий: {ctx['COMMENT'] or '—'}\n"
        "Напиши `подтверждаю` или пришли правки текстом."
    )
    return {
        "context": ctx,
        "reply": summary,
        "done": True,
        "await_input": True,
        "active_subgraph": "booking",
    }


async def finalize(state: BookingState) -> BookingState:
    ctx = state["context"]
    # here you can check slot / rules
    # booking_id = await create_booking(ctx)
    booking_id = 1111
    return {"reply": f"Готово! Бронь {booking_id}. ✅", "done": True}


def branch(s):
    t = (s.get("text") or "").strip().lower()

    print(
        f"DEBUG branch: text='{t}', done={s.get('done')}, await_input={s.get('await_input')}"
    )

    # If done and user confirms - finalize
    if s.get("done") and t == "подтверждаю":
        print("DEBUG: returning 'final'")
        return "final"

    # If done but no confirmation - exit to main graph to wait for confirmation
    if s.get("done") and not t:
        print("DEBUG: returning 'await' (done, waiting for confirmation)")
        return "await"

    # If there's text to process - continue
    if t:
        print("DEBUG: returning 'continue' (has text)")
        return "continue"

    # If no text - exit to main graph to wait for input
    print("DEBUG: returning 'await' (no text, exit to main graph)")
    return "await"


def build_booking_graph():
    g = StateGraph(BookingState)

    g.add_node("ask_or_fill", ask_or_fill)  # ask questions/LLM-parse/collect fields
    g.add_node("finalize", finalize)  # save booking, send result
    g.add_edge(START, "ask_or_fill")
    g.add_conditional_edges(
        "ask_or_fill",
        branch,
        {
            "final": "finalize",
            "await": END,  # Return to main graph for input waiting
            "continue": "ask_or_fill",
        },
    )

    g.add_edge("finalize", END)

    app = g.compile()
    gen_png_graph(app)
    return app


def gen_png_graph(app_obj, name_photo: str = "graph.png") -> None:
    with open(name_photo, "wb") as f:
        f.write(app_obj.get_graph().draw_mermaid_png())
