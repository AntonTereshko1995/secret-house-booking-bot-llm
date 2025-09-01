from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from core.logging import get_logger
from infrastructure.llm.graphs.app.app_graph_builder import build_app_graph

router = Router()
logger = get_logger(__name__)

# Create graph once on import
graph = build_app_graph()


@router.message(F.text.startswith("/start"))
async def start_command(message: types.Message):
    """Handler for /start command"""
    await message.answer(
        "Привет! Я бот для бронирования секретного дома. "
        "Напиши, что хочешь забронировать. "
        "Пример: «Хочу забронировать дом на 12.08 на 12 часов»."
    )


@router.message(F.text)
async def handle_message(message: types.Message, state: FSMContext):
    thread_id = f"{message.chat.id}:{message.from_user.id}"

    try:
        # Try to get previous state
        checkpoint = await graph.aget_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        previous_state = checkpoint.values if checkpoint else {}
        logger.info(f"Retrieved state for {thread_id}: {previous_state}")
    except Exception as e:
        logger.error(f"Error getting state for {thread_id}: {e}")
        previous_state = {}

    try:
        graph_state = {
            "user_id": message.from_user.id,
            "text": message.text,
            "active_subgraph": previous_state.get("active_subgraph"),
            "context": previous_state.get("context", {}),
            "intent": previous_state.get("intent"),
            "await_input": previous_state.get("await_input"),
            "done": previous_state.get("done"),
            "last_asked": previous_state.get("last_asked"),
        }

        logger.info(f"Graph state for {thread_id}: {graph_state}")

        # Get result from graph
        result = await graph.ainvoke(
            graph_state, config={"configurable": {"thread_id": thread_id}}
        )

        logger.info(f"Graph result for {thread_id}: {result}")

        # Send response
        reply = result.get("reply", "Извините, произошла ошибка")
        await message.answer(reply)

    except Exception as e:
        logger.error("Ошибка обработки сообщения", exc_info=e)
        await message.answer("Извините, произошла ошибка. Попробуйте позже.")
