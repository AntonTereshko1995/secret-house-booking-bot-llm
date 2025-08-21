from typing import Literal, TypedDict, Optional, Dict, Any


class AppState(TypedDict, total=False):
    user_id: int
    text: str
    intent: Literal["booking", "availability", "change", "price", "faq", "unknown"]
    active_subgraph: Optional[str]  # текущий активный подграф
    context: dict            # сюда складываем накопленные поля брони
    reply: str               # что отправить в чат
    await_input: Optional[bool]  # ожидает ли граф ввода от пользователя

class BookingState(TypedDict, total=False):
    context: dict       # копим поля здесь
    text: str           # последнее пользовательское сообщение
    reply: str          # ответ пользователю
    done: bool
