"""
Хендлеры для callback кнопок
"""

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from core.logging import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик всех callback запросов"""
    
    try:
        # Обрабатываем callback в зависимости от данных
        if callback.data == "cancel":
            await callback.message.edit_text("Действие отменено")
        elif callback.data == "help":
            await callback.message.edit_text(
                "Доступные команды:\n"
                "/start - Начать бронирование\n"
                "/help - Показать справку"
            )
        else:
            await callback.message.edit_text("Неизвестная команда")
            
        await callback.answer()
        
    except Exception as e:
        logger.error("Ошибка обработки callback", exc_info=e)
        await callback.answer("Произошла ошибка", show_alert=True)
