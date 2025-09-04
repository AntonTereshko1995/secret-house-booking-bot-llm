from typing import Literal, TypedDict


class AppState(TypedDict, total=False):
    user_id: int
    text: str
    intent: Literal["booking", "availability", "change", "price", "faq", "unknown"]
    active_subgraph: str | None  # current active subgraph
    context: dict  # accumulated booking fields
    reply: str  # what to send to chat
    await_input: bool | None  # whether graph awaits user input
    # FAQ-specific fields
    faq_data: dict | None  # FAQ response data
    faq_context: dict | None  # FAQ conversation context


class BookingState(TypedDict, total=False):
    context: dict  # accumulate fields here
    text: str  # last user message
    reply: str  # response to user
    done: bool
