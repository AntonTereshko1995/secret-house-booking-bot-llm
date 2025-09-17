from enum import Enum

from langgraph.graph import END, START, StateGraph

from core.config import settings
from core.utils.datetime_helper import (
    extract_date_from_natural_language,
    is_date,
    is_time,
    norm_date,
    norm_time,
)
from core.utils.string_helper import parse_yes_no
from domain.booking.payment import PaymentStatus
from application.services.pricing_service import PricingService
from infrastructure.llm.extractors import booking_extractor
from infrastructure.llm.graphs.common.graph_state import BookingState
from domain.booking.entities import Tariff


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
        BookingField.SECOND_BEDROOM,  # Сначала белая спальня (без доплаты)
        BookingField.FIRST_BEDROOM,   # Потом зеленая спальня (с доплатой)
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
    BookingField.FIRST_BEDROOM: "🟢 Зеленая спальня (основная спальня с большой кроватью)? (`да`/`нет`)",
    BookingField.SECOND_BEDROOM: "⚪ Белая спальня (дополнительная спальня)? (`да`/`нет`)",
    BookingField.SAUNA: "🧖‍♀️ Добавить сауну к бронированию? (`да`/`нет`)",
    BookingField.PHOTOSHOOT: "📸 Нужна фотосессия? (`да`/`нет`)",
    BookingField.SECRET_ROOM: "🚪 Добавить секретную комнату? (`да`/`нет`)",
    BookingField.NUMBER_GUESTS: "Количество гостей? Укажите число",
    BookingField.CONTACT: "Контакт для связи: укажите `@username` или телефон с `+`",
    BookingField.COMMENT: "Дополнительные пожелания или комментарий к брони? (напишите `нет` если нет комментариев)",
}

booking_extractor = booking_extractor.BookingExtractor()
pricing_service = PricingService()


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


def _convert_tariff_string_to_enum(tariff_str: str) -> Tariff | None:
    """Convert tariff string to Tariff enum value"""
    # Mapping from pricing extractor strings to enum values
    tariff_mapping = {
        "12 часов": Tariff.HOURS_12,
        "суточно от 3 человек": Tariff.DAY,
        "сутки": Tariff.DAY,
        "сутки от 3": Tariff.DAY,
        "сутки для двоих": Tariff.DAY_FOR_COUPLE,
        "сутночно для двоих": Tariff.DAY_FOR_COUPLE,
        "рабочий": Tariff.WORKER,
        "инкогнито день": Tariff.INCOGNITA_DAY,
        "инкогнито 12": Tariff.INCOGNITA_HOURS,
        "абонемент 3": Tariff.DAY,  # Default to DAY for subscription
        "абонемент 5": Tariff.DAY,
        "абонемент 8": Tariff.DAY,
    }
    
    if tariff_str in tariff_mapping:
        return tariff_mapping[tariff_str]
    
    # Try fuzzy matching for common variations
    tariff_str_lower = tariff_str.lower()
    
    if "12" in tariff_str_lower and ("час" in tariff_str_lower or "полсуток" in tariff_str_lower):
        return Tariff.HOURS_12
    elif any(word in tariff_str_lower for word in ["сутки", "день", "суточн"]):
        if any(word in tariff_str_lower for word in ["двоих", "2", "пара", "couple"]):
            return Tariff.DAY_FOR_COUPLE
        else:
            return Tariff.DAY
    elif "рабоч" in tariff_str_lower or "work" in tariff_str_lower:
        return Tariff.WORKER
    elif "инкогнит" in tariff_str_lower:
        if "12" in tariff_str_lower or "час" in tariff_str_lower:
            return Tariff.INCOGNITA_HOURS
        else:
            return Tariff.INCOGNITA_DAY
    
    return None

async def get_dynamic_question(field: BookingField, tariff_enum: Tariff | None = None) -> str:
    """Get dynamic question with pricing based on selected tariff"""
    # For non-pricing fields, use static questions
    if field not in {BookingField.SAUNA, BookingField.SECRET_ROOM, BookingField.SECOND_BEDROOM, BookingField.FIRST_BEDROOM, BookingField.PHOTOSHOOT}:
        return QUESTIONS.get(field, f"Укажите {field.value}")
    
    # If no tariff selected yet, use static questions
    if tariff_enum is None:
        return QUESTIONS.get(field, f"Укажите {field.value}")
    
    # Get pricing for the selected tariff
    try:
        tariff_rate = await pricing_service.get_tariff_by_id(tariff_enum.value)
        if not tariff_rate:
            # Fallback to static questions if tariff not found
            return QUESTIONS.get(field, f"Укажите {field.value}")
        
        # Generate dynamic questions with real prices
        if field == BookingField.SAUNA:
            if tariff_rate.sauna_price > 0:
                return f"🧖‍♀️ Добавить сауну к бронированию +{tariff_rate.sauna_price} бел.руб? (`да`/`нет`)"
            else:
                return f"🧖‍♀️ Добавить сауну к бронированию (включена в тариф)? (`да`/`нет`)"
        
        elif field == BookingField.SECRET_ROOM:
            if tariff_rate.secret_room_price > 0:
                return f"🚪 Добавить секретную комнату +{tariff_rate.secret_room_price} бел.руб? (`да`/`нет`)"
            else:
                return f"🚪 Добавить секретную комнату (включена в тариф)? (`да`/`нет`)"
        
        elif field == BookingField.SECOND_BEDROOM:
            # White bedroom - asked first, shows actual price from config
            if tariff_rate.second_bedroom_price > 0:
                return f"⚪ Белая спальня (дополнительная спальня) +{tariff_rate.second_bedroom_price} бел.руб? (`да`/`нет`)"
            else:
                return f"⚪ Белая спальня (дополнительная спальня) - включена в тариф? (`да`/`нет`)"
        
        elif field == BookingField.FIRST_BEDROOM:
            # Green bedroom - main bedroom, always included in tariff (no additional cost)
            return f"🟢 Зеленая спальня (основная спальня) - включена в тариф? (`да`/`нет`)"
        
        elif field == BookingField.PHOTOSHOOT:
            if tariff_rate.photoshoot_price > 0:
                return f"📸 Нужна фотосессия +{tariff_rate.photoshoot_price} бел.руб? (`да`/`нет`)"
            else:
                return f"📸 Нужна фотосессия (включена в тариф)? (`да`/`нет`)"
    
    except Exception as e:
        print(f"DEBUG: Error getting dynamic question for {field}: {e}")
        # Fallback to static question on error
        return QUESTIONS.get(field, f"Укажите {field.value}")
    
    # Fallback to static question
    return QUESTIONS.get(field, f"Укажите {field.value}")

def _first_missing(ctx: dict) -> BookingField | None:
    print(f"DEBUG _first_missing: ctx keys = {list(ctx.keys())}")

    # Always check tariff first
    if BookingField.TARIFF.value not in ctx or ctx[BookingField.TARIFF.value] is None:
        print("DEBUG: missing TARIFF")
        return BookingField.TARIFF

    # Get required fields for the selected tariff
    tariff_value = ctx[BookingField.TARIFF.value]

    # Convert tariff to enum if it's stored as string or int
    if isinstance(tariff_value, str):
        # First try direct string to enum conversion
        tariff_enum = _convert_tariff_string_to_enum(tariff_value)
        if tariff_enum is None:
            # Try if it's a string number
            if tariff_value.isdigit():
                try:
                    tariff_enum = Tariff(int(tariff_value))
                except ValueError:
                    print(f"DEBUG: Invalid tariff number: {tariff_value}")
                    tariff_enum = None
            else:
                print(f"DEBUG: Unknown tariff format: {tariff_value}")
                tariff_enum = None
    elif isinstance(tariff_value, int):
        try:
            tariff_enum = Tariff(tariff_value)
        except ValueError:
            print(f"DEBUG: Invalid tariff value: {tariff_value}")
            tariff_enum = None
    else:
        tariff_enum = tariff_value

    # If we still don't have a valid tariff enum, return empty required list to avoid errors
    if tariff_enum is None:
        print(f"DEBUG: Could not convert tariff '{tariff_value}' to enum, using base requirements only")
        required_fields = BASE_REQUIRED
    else:
        required_fields = RATE_REQUIREMENTS.get(tariff_enum, []) + BASE_REQUIRED
        print(f"DEBUG: Using tariff enum {tariff_enum}, required fields: {[f.value for f in required_fields]}")

    for field in required_fields:
        field_key = field.value
        # Special case for COMMENT: None is a valid value (means "no comment")
        if field == BookingField.COMMENT:
            if field_key not in ctx:
                print(f"DEBUG: missing field '{field}' for tariff '{tariff_enum}'")
                return field
        else:
            if field_key not in ctx or ctx[field_key] in (None, ""):
                print(f"DEBUG: missing field '{field}' for tariff '{tariff_enum}'")
                return field
    print("DEBUG: no missing fields")
    return None


def _handle_summary_mode_input(text: str, was_done: bool) -> str:
    """Handle user input when booking summary was already shown"""
    if not (was_done and text):
        return text
    
    standard_no_responses = {"нет", "no", "-", "не надо", "не нужно", "none"}
    
    # If user wants to confirm, keep the text as is
    if text.lower() == "подтверждаю":
        return text
    
    # If user sends standard 'no' response, ignore it (probably answering final questions)
    if text.lower() in standard_no_responses:
        print(f"DEBUG: Ignoring standard 'no' response in summary mode: '{text}'")
        return text
    
    # User wants to modify something - clear text to restart the flow
    print(f"DEBUG: User wants to modify booking, resetting done state. Text: '{text}'")
    return ""


async def _process_user_text(ctx: dict, text: str) -> dict:
    """Process user input to extract booking information"""
    # 1) Try LLM parser first
    try:
        parsed = await booking_extractor.aextract(text)
        if parsed:
            ctx.update(parsed)
    except Exception:
        pass

    # 2) Manual parsing for specific fields
    missing_field = _first_missing(ctx)
    if missing_field:
        print(f"DEBUG: processing field {missing_field} with text '{text}'")
        ctx = _parse_field_value(ctx, missing_field, text)
    
    return ctx


def _parse_field_value(ctx: dict, field: BookingField, text: str) -> dict:
    """Parse specific field value from user text"""
    if field == BookingField.TARIFF:
        print(f"DEBUG TARIFF processing: text='{text}'")
        tariff = parse_tariff_from_text(text)
        if tariff is not None:
            print(f"DEBUG: setting TARIFF to '{tariff}'")
            ctx[field.value] = tariff
        else:
            print("DEBUG: no TARIFF match found")
    
    elif field in {
        BookingField.FIRST_BEDROOM,
        BookingField.SECOND_BEDROOM,
        BookingField.SAUNA,
        BookingField.PHOTOSHOOT,
        BookingField.SECRET_ROOM,
    }:
        v = parse_yes_no(text)
        if v is not None:
            # Special handling for bedrooms
            if field in {BookingField.FIRST_BEDROOM, BookingField.SECOND_BEDROOM}:
                ctx = _handle_bedroom_logic(ctx, field, v)
            else:
                ctx[field.value] = v
    
    elif field in {BookingField.START_DATE, BookingField.FINISH_DATE}:
        if is_date(text):
            ctx[field.value] = norm_date(text)
        else:
            # Try to extract date from natural language
            extracted_date = extract_date_from_natural_language(text)
            if extracted_date:
                ctx[field.value] = extracted_date
                print(f"DEBUG: extracted date '{extracted_date}' from natural language")
    
    elif field in {BookingField.START_TIME, BookingField.FINISH_TIME} and is_time(text):
        ctx[field.value] = norm_time(text)
    
    elif field == BookingField.NUMBER_GUESTS and text.isdigit() and int(text) > 0:
        ctx[field.value] = int(text)
    
    elif field == BookingField.CONTACT and (text.startswith("@") or text.startswith("+")):
        ctx[field.value] = text
    
    elif field == BookingField.COMMENT:
        ctx[field.value] = None if text.lower() in {"нет", "no", "-"} else text
    
    return ctx

def _handle_bedroom_logic(ctx: dict, field: BookingField, value: bool) -> dict:
    """Handle special bedroom selection logic"""
    if field == BookingField.SECOND_BEDROOM:  # Белая спальня
        ctx[field.value] = value
        
        # Если пользователь сказал НЕТ белой спальне, автоматически выбираем зеленую
        if not value:
            ctx[BookingField.FIRST_BEDROOM.value] = True
            print("DEBUG: User declined white bedroom, automatically selecting green bedroom")
        
    elif field == BookingField.FIRST_BEDROOM:  # Зеленая спальня
        # Зеленая спальня спрашивается только если была выбрана белая
        ctx[field.value] = value
    
    return ctx


async def _ask_for_missing_field(ctx: dict, field: BookingField) -> BookingState:
    """Ask user for a missing booking field"""
    print(f"DEBUG ask_or_fill: asking for {field}")
    print(f"DEBUG: current context keys: {list(ctx.keys())}")
    
    # Get current tariff for dynamic pricing questions
    tariff_enum = _get_tariff_enum_from_context(ctx)
    
    # Get dynamic question with pricing info
    question = await get_dynamic_question(field, tariff_enum)
    
    return {
        "context": ctx,
        "text": "",
        "reply": question,
        "done": False,
        "await_input": False,
        "last_asked": field.value,
        "active_subgraph": "booking",
    }


def _get_tariff_enum_from_context(ctx: dict) -> Tariff | None:
    """Extract tariff enum from booking context"""
    if BookingField.TARIFF.value not in ctx or ctx[BookingField.TARIFF.value] is None:
        return None
    
    tariff_value = ctx[BookingField.TARIFF.value]
    
    if isinstance(tariff_value, str):
        tariff_enum = _convert_tariff_string_to_enum(tariff_value)
        if tariff_enum is None and tariff_value.isdigit():
            try:
                tariff_enum = Tariff(int(tariff_value))
            except ValueError:
                pass
        return tariff_enum
    elif isinstance(tariff_value, int):
        try:
            return Tariff(tariff_value)
        except ValueError:
            pass
    
    return None


async def _generate_booking_summary(ctx: dict) -> BookingState:
    """Generate booking summary when all fields are collected"""
    tariff = ctx[BookingField.TARIFF.value]
    
    # Convert tariff to enum for RATE_REQUIREMENTS lookup
    tariff_enum = _get_tariff_enum_from_context(ctx)
    required_fields = RATE_REQUIREMENTS.get(tariff_enum, []) + BASE_REQUIRED

    summary = _format_booking_summary(ctx, tariff, required_fields)
    
    return {
        "context": ctx,
        "reply": summary,
        "done": True,
        "await_input": True,
        "active_subgraph": "booking",
    }


def _format_booking_summary(ctx: dict, tariff: str, required_fields: list) -> str:
    """Format booking summary text"""
    rate_display = get_rate_display_name(tariff)
    summary_lines = ["📋 Резюме заявки:", f"Тариф: {rate_display}"]

    # Add dates and times (always present)
    if BookingField.START_DATE in required_fields:
        summary_lines.extend([
            f"Заезд: {ctx[BookingField.START_DATE.value]} {ctx[BookingField.START_TIME.value]}",
            f"Выезд: {ctx[BookingField.FINISH_DATE.value]} {ctx[BookingField.FINISH_TIME.value]}"
        ])

    # Add optional fields based on tariff
    _add_optional_fields_to_summary(summary_lines, ctx, required_fields)

    # Always add contact and comment
    summary_lines.extend([
        f"Контакт: {ctx[BookingField.CONTACT.value]}",
        f"Комментарий: {ctx[BookingField.COMMENT.value] or '—'}",
        "Напиши `подтверждаю` или пришли правки текстом.",
    ])

    return "\n".join(summary_lines)


def _add_optional_fields_to_summary(summary_lines: list, ctx: dict, required_fields: list):
    """Add optional booking fields to summary"""
    field_mappings = [
        (BookingField.FIRST_BEDROOM, "🟢 Зеленая спальня"),
        (BookingField.SECOND_BEDROOM, "⚪ Белая спальня"), 
        (BookingField.SAUNA, "🧖‍♀️ Сауна"),
        (BookingField.PHOTOSHOOT, "📸 Фотосъёмка"),
        (BookingField.SECRET_ROOM, "🚪 Секретная комната"),
    ]
    
    for field, label in field_mappings:
        if field in required_fields:
            value = "да" if ctx[field.value] else "нет"
            summary_lines.append(f"{label}: {value}")
    
    if BookingField.NUMBER_GUESTS in required_fields:
        summary_lines.append(f"👥 Гостей: {ctx[BookingField.NUMBER_GUESTS.value]}")

async def ask_or_fill(state: BookingState) -> BookingState:
    """Main booking flow handler - processes user input and manages conversation state"""
    ctx = dict(state.get("context", {}))
    text = (state.get("text") or "").strip()
    was_done = state.get("done", False)

    # Handle user input when booking was already complete (summary mode)
    text = _handle_summary_mode_input(text, was_done)
    
    # Process any incoming text to extract booking information
    if text:
        ctx = await _process_user_text(ctx, text)

    # Check if we need more information
    missing_field = _first_missing(ctx)
    if missing_field:
        return await _ask_for_missing_field(ctx, missing_field)

    # All information collected - show booking summary
    return await _generate_booking_summary(ctx)


async def payment_request(state: BookingState) -> BookingState:
    """Show payment details and request proof"""
    ctx = state.get("context", {})

    # Get total cost if available (could be calculated from context or passed separately)
    total_cost = ctx.get("total_cost", "Рассчитывается")

    payment_message = f"""💳 Оплата бронирования

Переведите сумму на карту: {settings.payment_card_number}
Или на телефон: {settings.payment_phone_number}

Сумма: {total_cost} BYN

📸 Пришлите скриншот или документ об оплате"""

    return {
        "context": ctx,
        "reply": payment_message,
        "payment_status": PaymentStatus.PENDING.value,
        "await_input": True,
        "active_subgraph": "booking",
        "done": False,  # Not fully done yet, waiting for payment proof
    }


async def finalize(state: BookingState) -> BookingState:
    """Finalize booking after payment confirmation"""
    # here you can check slot / rules and create actual booking
    # booking_id = await create_booking(state["context"])
    _ = state  # Acknowledge parameter usage for linter
    booking_id = 1111

    return {
        "reply": f"✅ Готово! Ваше бронирование #{booking_id} подтверждено и ожидает проверки администратором.",
        "done": True,
        "payment_status": PaymentStatus.PROOF_UPLOADED.value,
    }


def branch(s):
    t = (s.get("text") or "").strip().lower()
    payment_status = s.get("payment_status")

    print(
        f"DEBUG branch: text='{t}', done={s.get('done')}, payment_status='{payment_status}', await_input={s.get('await_input')}"
    )

    # If payment proof uploaded - finalize booking
    if payment_status == PaymentStatus.PROOF_UPLOADED.value:
        print("DEBUG: returning 'final' (payment proof uploaded)")
        return "final"

    # If done and user confirms - go to payment request
    if s.get("done") and t == "подтверждаю":
        print("DEBUG: returning 'payment' (user confirmed booking)")
        return "payment"

    # If payment pending and no text - exit to await payment proof
    if payment_status == PaymentStatus.PENDING.value and not t:
        print("DEBUG: returning 'await' (waiting for payment proof)")
        return "await"

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
    g.add_node("payment_request", payment_request)  # show payment details
    g.add_node("finalize", finalize)  # save booking, send result
    g.add_edge(START, "ask_or_fill")
    g.add_conditional_edges(
        "ask_or_fill",
        branch,
        {
            "payment": "payment_request",  # user confirmed booking, show payment
            "final": "finalize",  # payment proof uploaded, finalize
            "await": END,  # Return to main graph for input waiting
            "continue": "ask_or_fill",  # continue collecting booking info
        },
    )

    # After payment request, return to main graph to await payment proof
    g.add_edge("payment_request", END)
    g.add_edge("finalize", END)

    app = g.compile()
    gen_png_graph(app)
    return app


def gen_png_graph(app_obj, name_photo: str = "graph.png") -> None:
    with open(name_photo, "wb") as f:
        f.write(app_obj.get_graph().draw_mermaid_png())
