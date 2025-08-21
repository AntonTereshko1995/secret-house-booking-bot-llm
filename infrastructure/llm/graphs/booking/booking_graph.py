from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from core.utils.datetime_helper import is_date, is_time, norm_date, norm_time
from halper.string_halper import parse_yes_no
from infrastructure.llm.extractors import booking_extractor
from infrastructure.llm.graphs.common.graph_state import BookingState

REQUIRED = ["TARIFF","START_DATE","START_TIME","FINISH_DATE","FINISH_TIME",
            "FIRST_BEDROOM","SECOND_BEDROOM","SAUNA","PHOTOSHOOT","SECRET_ROOM",
            "NUMBER_GUESTS","CONTACT","COMMENT"]
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
    "COMMENT": "Комментарий к брони (или напиши `нет`)."
    }

booking_extractor = booking_extractor.BookingExtractor()

def _first_missing(ctx: dict) -> Optional[str]:
    for f in REQUIRED:
        if f not in ctx or ctx[f] in (None,""):
            return f
    return None

async def ask_or_fill(state: BookingState) -> BookingState:
    ctx = dict(state.get("context", {}))
    text = (state.get("text") or "").strip()

    # 1) Сначала пробуем LLM-парсер: он может вытащить сразу пачку полей
    if text:
        try:
            parsed = await booking_extractor.aextract(text)
            if parsed:
                ctx.update(parsed)
        except Exception:
            # don't crash flow if LLM is unavailable - just continue
            pass

    # 2) Строгое дозаполнение текущего недостающего поля по ответу пользователя
    miss = _first_missing(ctx)
    if miss:
        if miss == "TARIFF":
            low = text.lower()
            if "12" in low:
                ctx[miss] = "12 часов"
            elif "сут" in low or "24" in low or "день" in low:
                ctx[miss] = "1 сутки"
        elif miss in {"FIRST_BEDROOM","SECOND_BEDROOM","SAUNA","PHOTOSHOOT","SECRET_ROOM"}:
            v=parse_yes_no(text); 
            if v is not None: ctx[miss]=v
        elif miss in {"START_DATE","FINISH_DATE"} and is_date(text):
            ctx[miss]=norm_date(text)
        elif miss in {"START_TIME","FINISH_TIME"} and is_time(text):
            ctx[miss]=norm_time(text)
        elif miss=="NUMBER_GUESTS" and text.isdigit() and int(text)>0:
            ctx[miss]=int(text)
        elif miss=="CONTACT" and (text.startswith("@") or text.startswith("+")):
            ctx[miss]=text
        elif miss=="COMMENT":
            ctx[miss]=None if text.lower() in {"нет","no","-"} else text

    # 3) If still missing - ask next specific question
    miss = _first_missing(ctx)
    if miss:
        return {
            "context": ctx,
            "reply": QUESTIONS[miss],
            "done": False,
            "await_input": True,
            "last_asked": miss,
            "active_subgraph": "booking"  # Add for propagation to main graph
        }

    # 4) All fields collected - show summary and wait for "confirm"
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
            "await_input": True,  # ← это читает branch() и уводит в END
            "active_subgraph": "booking"  # Add for propagation to main graph
        }

async def finalize(state: BookingState)->BookingState:
    ctx = state["context"]
    # here you can check slot / rules
    # booking_id = await create_booking(ctx)
    booking_id = 1111
    return {"reply": f"Готово! Бронь {booking_id}. ✅", "done": True}

def branch(s):
    t = (s.get("text") or "").strip().lower()
    if s.get("done") and t == "подтверждаю":
        return "final"

    if s.get("await_input"):
        return "await"     # → возврат в основной граф

    return "continue"

def build_booking_graph():
    g = StateGraph(BookingState)

    g.add_node("ask_or_fill", ask_or_fill)  # ask questions/LLM-parse/collect fields
    g.add_node("finalize", finalize)        # save booking, send result
    g.add_edge(START, "ask_or_fill")
    g.add_conditional_edges(
        "ask_or_fill",  
        branch,
        {
            "final": "finalize",
            "await": END,           # ✅ return to main graph for input waiting
            "continue": "ask_or_fill",
        },
    )

    g.add_edge("finalize", END) 

    memory = MemorySaver()
    app = g.compile(checkpointer=memory)
    gen_png_graph(app)
    return app

def gen_png_graph(app_obj, name_photo: str = "graph.png") -> None:
    """
    Generates PNG image of the graph and saves it to file.
    
    Args:
        app_obj: Compiled graph object
        name_photo: File name for saving (default "graph.png")
    """
    with open(name_photo, "wb") as f:
        f.write(app_obj.get_graph().draw_mermaid_png())
