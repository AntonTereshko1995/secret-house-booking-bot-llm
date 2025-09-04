from enum import Enum

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


class Tariff(Enum):
    HOURS_12 = 0
    DAY = 1
    WORKER = 2
    INCOGNITA_DAY = 3
    INCOGNITA_HOURS = 4
    DAY_FOR_COUPLE = 5


class BookingField(Enum):
    TARIFF = "TARIFF"
    START_DATE = "START_DATE"
    START_TIME = "START_TIME"
    FINISH_DATE = "FINISH_DATE"
    FINISH_TIME = "FINISH_TIME"
    FIRST_BEDROOM = "FIRST_BEDROOM"
    SECOND_BEDROOM = "SECOND_BEDROOM"
    SAUNA = "SAUNA"
    PHOTOSHOOT = "PHOTOSHOOT"
    SECRET_ROOM = "SECRET_ROOM"
    NUMBER_GUESTS = "NUMBER_GUESTS"
    CONTACT = "CONTACT"
    COMMENT = "COMMENT"


# Define required fields for each rate type
RATE_REQUIREMENTS = {
    Tariff.DAY: [
        BookingField.SAUNA,
        BookingField.PHOTOSHOOT,
        BookingField.START_DATE,
        BookingField.START_TIME,
        BookingField.FINISH_DATE,
        BookingField.FINISH_TIME,
        BookingField.NUMBER_GUESTS,
    ],
    Tariff.DAY_FOR_COUPLE: [
        BookingField.SAUNA,
        BookingField.PHOTOSHOOT,
        BookingField.START_DATE,
        BookingField.START_TIME,
        BookingField.FINISH_DATE,
        BookingField.FINISH_TIME,
    ],
    Tariff.HOURS_12: [
        BookingField.SAUNA,
        BookingField.SECRET_ROOM,
        BookingField.FIRST_BEDROOM,
        BookingField.SECOND_BEDROOM,
        BookingField.START_DATE,
        BookingField.START_TIME,
        BookingField.FINISH_DATE,
        BookingField.FINISH_TIME,
        BookingField.NUMBER_GUESTS,
    ],
    Tariff.WORKER: [
        BookingField.SAUNA,
        BookingField.SECRET_ROOM,
        BookingField.FIRST_BEDROOM,
        BookingField.SECOND_BEDROOM,
        BookingField.START_DATE,
        BookingField.START_TIME,
        BookingField.FINISH_DATE,
        BookingField.FINISH_TIME,
        BookingField.NUMBER_GUESTS,
    ],
    Tariff.INCOGNITA_HOURS: [
        BookingField.PHOTOSHOOT,
        BookingField.START_DATE,
        BookingField.START_TIME,
        BookingField.FINISH_DATE,
        BookingField.FINISH_TIME,
        BookingField.NUMBER_GUESTS,
    ],
    Tariff.INCOGNITA_DAY: [
        BookingField.PHOTOSHOOT,
        BookingField.START_DATE,
        BookingField.START_TIME,
        BookingField.FINISH_DATE,
        BookingField.FINISH_TIME,
        BookingField.NUMBER_GUESTS,
    ],
}

# Base required fields for all bookings
BASE_REQUIRED = [BookingField.TARIFF, BookingField.CONTACT, BookingField.COMMENT]
QUESTIONS = {
    BookingField.TARIFF: "Выберите тариф:\n\n👥 `1` - Суточно от 3-ех человек (от 3 гостей)\n💑 `5` - Суточно для пар (для двоих)\n⏰ `0` - 12 часов (дневное бронирование)\n💼 `2` - Рабочий (будни Пн-Чт)\n🕶️ `4` - Инкогнито 12 часов (VIP на 12ч)\n🕶️ `3` - Инкогнито на сутки (VIP посуточно)",
    BookingField.START_DATE: "Дата заезда? Укажите в формате `ДД.ММ` или `ДД.ММ.ГГГГ`",
    BookingField.START_TIME: "Время заезда? Укажите в формате `ЧЧ:ММ`",
    BookingField.FINISH_DATE: "Дата выезда? Укажите в формате `ДД.ММ` или `ДД.ММ.ГГГГ`",
    BookingField.FINISH_TIME: "Время выезда? Укажите в формате `ЧЧ:ММ`",
    BookingField.FIRST_BEDROOM: "Выбор основной спальни? (`да`/`нет`)",
    BookingField.SECOND_BEDROOM: "Выбор дополнительной спальни? (`да`/`нет`)",
    BookingField.SAUNA: "Добавить сауну к бронированию? (`да`/`нет`)",
    BookingField.PHOTOSHOOT: "Нужна фотосессия? (`да`/`нет`)",
    BookingField.SECRET_ROOM: "Добавить секретную комнату? (`да`/`нет`)",
    BookingField.NUMBER_GUESTS: "Количество гостей? Укажите число",
    BookingField.CONTACT: "Контакт для связи: укажите `@username` или телефон с `+`",
    BookingField.COMMENT: "Дополнительные пожелания или комментарий к брони? (напишите `нет` если нет комментариев)",
}

booking_extractor = booking_extractor.BookingExtractor()


def get_rate_display_name(tariff: Tariff) -> str:
    """Get display name for rate type"""
    rate_names = {
        Tariff.DAY: "СУТОЧНО ОТ 3 ЛЮДЕЙ",
        Tariff.DAY_FOR_COUPLE: "СУТОЧНО ДЛЯ ПАР",
        Tariff.HOURS_12: "12 ЧАСОВ",
        Tariff.WORKER: "РАБОЧИЙ (Пн-Чт)",
        Tariff.INCOGNITA_HOURS: "ИНКОГНИТО 12 ЧАСОВ",
        Tariff.INCOGNITA_DAY: "ИНКОГНИТО НА СУТКИ",
    }
    return rate_names.get(tariff, str(tariff))


def parse_tariff_from_text(text: str) -> Tariff | None:
    """Parse tariff from user input text"""
    low = text.lower().strip()

    # Try to parse numeric value first
    if low.isdigit():
        try:
            value = int(low)
            return Tariff(value)
        except ValueError:
            pass

    # Parse by keywords
    if "12" in low and "инкогнито" not in low:
        return Tariff.HOURS_12
    elif "инкогнито" in low and "12" in low:
        return Tariff.INCOGNITA_HOURS
    elif "инкогнито" in low and ("сут" in low or "24" in low or "день" in low):
        return Tariff.INCOGNITA_DAY
    elif "суточно" in low and ("пар" in low or "два" in low or "2" in low):
        return Tariff.DAY_FOR_COUPLE
    elif "суточно" in low and (
        "3" in low or "трех" in low or "трёх" in low or "от 3" in low
    ):
        return Tariff.DAY
    elif "рабочий" in low or "работа" in low:
        return Tariff.WORKER
    elif "сут" in low or "24" in low or "день" in low:
        return Tariff.DAY_FOR_COUPLE  # Default daily rate

    return None


def _first_missing(ctx: dict) -> BookingField | None:
    print(f"DEBUG _first_missing: ctx keys = {list(ctx.keys())}")

    # Always check tariff first
    if BookingField.TARIFF.value not in ctx or ctx[BookingField.TARIFF.value] is None:
        print("DEBUG: missing TARIFF")
        return BookingField.TARIFF

    # Get required fields for the selected tariff
    tariff = ctx[BookingField.TARIFF.value]
    required_fields = RATE_REQUIREMENTS.get(tariff, []) + BASE_REQUIRED

    for field in required_fields:
        field_key = field.value
        if field_key not in ctx or ctx[field_key] in (None, ""):
            print(f"DEBUG: missing field '{field}' for tariff '{tariff}'")
            return field
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
            if miss == BookingField.TARIFF:
                print(f"DEBUG TARIFF processing: text='{text}'")
                tariff = parse_tariff_from_text(text)
                if tariff is not None:
                    print(f"DEBUG: setting TARIFF to '{tariff}'")
                    ctx[miss.value] = tariff
                else:
                    print("DEBUG: no TARIFF match found")
            elif miss in {
                BookingField.FIRST_BEDROOM,
                BookingField.SECOND_BEDROOM,
                BookingField.SAUNA,
                BookingField.PHOTOSHOOT,
                BookingField.SECRET_ROOM,
            }:
                v = parse_yes_no(text)
                if v is not None:
                    ctx[miss.value] = v
            elif miss in {BookingField.START_DATE, BookingField.FINISH_DATE}:
                # Try exact date format first
                if is_date(text):
                    ctx[miss.value] = norm_date(text)
                else:
                    # Try to extract date from natural language
                    extracted_date = extract_date_from_natural_language(text)
                    if extracted_date:
                        ctx[miss.value] = extracted_date
                        print(
                            f"DEBUG: extracted date '{extracted_date}' from natural language"
                        )
            elif miss in {
                BookingField.START_TIME,
                BookingField.FINISH_TIME,
            } and is_time(text):
                ctx[miss.value] = norm_time(text)
            elif (
                miss == BookingField.NUMBER_GUESTS and text.isdigit() and int(text) > 0
            ):
                ctx[miss.value] = int(text)
            elif miss == BookingField.CONTACT and (
                text.startswith("@") or text.startswith("+")
            ):
                ctx[miss.value] = text
            elif miss == BookingField.COMMENT:
                ctx[miss.value] = None if text.lower() in {"нет", "no", "-"} else text

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
            "last_asked": miss.value,
            "active_subgraph": "booking",
        }

    # All fields collected - show summary and wait for "confirm"
    tariff = ctx[BookingField.TARIFF.value]
    required_fields = RATE_REQUIREMENTS.get(tariff, []) + BASE_REQUIRED

    rate_display = get_rate_display_name(tariff)
    summary_lines = ["📋 Резюме заявки:", f"Тариф: {rate_display}"]

    # Add dates and times (always present)
    if BookingField.START_DATE in required_fields:
        summary_lines.append(
            f"Заезд: {ctx[BookingField.START_DATE.value]} {ctx[BookingField.START_TIME.value]}"
        )
        summary_lines.append(
            f"Выезд: {ctx[BookingField.FINISH_DATE.value]} {ctx[BookingField.FINISH_TIME.value]}"
        )

    # Add optional fields based on tariff
    if BookingField.FIRST_BEDROOM in required_fields:
        summary_lines.append(
            f"1-я спальня: {'да' if ctx[BookingField.FIRST_BEDROOM.value] else 'нет'}"
        )
    if BookingField.SECOND_BEDROOM in required_fields:
        summary_lines.append(
            f"2-я спальня: {'да' if ctx[BookingField.SECOND_BEDROOM.value] else 'нет'}"
        )
    if BookingField.SAUNA in required_fields:
        summary_lines.append(
            f"Сауна: {'да' if ctx[BookingField.SAUNA.value] else 'нет'}"
        )
    if BookingField.PHOTOSHOOT in required_fields:
        summary_lines.append(
            f"Фотосъёмка: {'да' if ctx[BookingField.PHOTOSHOOT.value] else 'нет'}"
        )
    if BookingField.SECRET_ROOM in required_fields:
        summary_lines.append(
            f"Секретная: {'да' if ctx[BookingField.SECRET_ROOM.value] else 'нет'}"
        )
    if BookingField.NUMBER_GUESTS in required_fields:
        summary_lines.append(f"Гостей: {ctx[BookingField.NUMBER_GUESTS.value]}")

    # Always add contact and comment
    summary_lines.extend(
        [
            f"Контакт: {ctx[BookingField.CONTACT.value]}",
            f"Комментарий: {ctx[BookingField.COMMENT.value] or '—'}",
            "Напиши `подтверждаю` или пришли правки текстом.",
        ]
    )

    summary = "\n".join(summary_lines)
    return {
        "context": ctx,
        "reply": summary,
        "done": True,
        "await_input": True,
        "active_subgraph": "booking",
    }


async def finalize(state: BookingState) -> BookingState:
    # here you can check slot / rules
    # booking_id = await create_booking(state["context"])
    _ = state  # Acknowledge parameter usage for linter
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
