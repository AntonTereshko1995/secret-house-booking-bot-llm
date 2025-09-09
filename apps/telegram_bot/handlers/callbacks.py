"""
Хендлеры для callback кнопок
"""

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext

from core.config import settings
from core.logging import get_logger
from domain.booking.payment import PaymentStatus
from infrastructure.notifications.admin_service import AdminNotificationService

router = Router()
logger = get_logger(__name__)


@router.callback_query(lambda c: c.data.startswith("approve:"))
async def handle_admin_approval(callback: types.CallbackQuery):
    """Handle admin booking approval"""
    try:
        booking_id = callback.data.split(":")[1]
        admin_username = callback.from_user.username or str(callback.from_user.id)
        
        logger.info(f"Admin {admin_username} approved booking {booking_id}")
        
        # Update admin message to show action taken
        await callback.message.edit_text(
            f"{callback.message.text}\n\n✅ ПОДТВЕРЖДЕНО админом @{admin_username}",
            reply_markup=None
        )
        
        # TODO: Here you would typically:
        # 1. Update booking status in database
        # 2. Get user chat ID from booking
        # 3. Send confirmation message to user
        # For now, we'll send a placeholder response
        
        await callback.answer("✅ Бронирование подтверждено", show_alert=True)
        
        # Send update notification to admin chat
        admin_service = AdminNotificationService(callback.bot, settings.admin_chat_id)
        await admin_service.notify_booking_updated(booking_id, "подтверждено", admin_username)
        
    except Exception as e:
        logger.error(f"Error handling admin approval: {e}")
        await callback.answer("Произошла ошибка при подтверждении", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("cancel:"))
async def handle_admin_cancellation(callback: types.CallbackQuery):
    """Handle admin booking cancellation"""
    try:
        booking_id = callback.data.split(":")[1]
        admin_username = callback.from_user.username or str(callback.from_user.id)
        
        logger.info(f"Admin {admin_username} cancelled booking {booking_id}")
        
        # Update admin message to show action taken
        await callback.message.edit_text(
            f"{callback.message.text}\n\n❌ ОТМЕНЕНО админом @{admin_username}",
            reply_markup=None
        )
        
        # TODO: Here you would typically:
        # 1. Update booking status in database
        # 2. Get user chat ID from booking  
        # 3. Send cancellation message to user
        
        await callback.answer("❌ Бронирование отменено", show_alert=True)
        
        # Send update notification to admin chat
        admin_service = AdminNotificationService(callback.bot, settings.admin_chat_id)
        await admin_service.notify_booking_updated(booking_id, "отменено", admin_username)
        
    except Exception as e:
        logger.error(f"Error handling admin cancellation: {e}")
        await callback.answer("Произошла ошибка при отмене", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("change_cost:"))
async def handle_admin_change_cost(callback: types.CallbackQuery):
    """Handle admin cost change request"""
    try:
        booking_id = callback.data.split(":")[1]
        admin_username = callback.from_user.username or str(callback.from_user.id)
        
        logger.info(f"Admin {admin_username} requested cost change for booking {booking_id}")
        
        # TODO: Implement cost change interface
        # This would typically show an inline form or ask for new cost
        
        await callback.answer(
            "💰 Функция изменения стоимости в разработке. Свяжитесь с разработчиком.",
            show_alert=True
        )
        
        # Send update notification to admin chat
        admin_service = AdminNotificationService(callback.bot, settings.admin_chat_id)
        await admin_service.notify_booking_updated(booking_id, "запрос изменения стоимости", admin_username)
        
    except Exception as e:
        logger.error(f"Error handling admin cost change: {e}")
        await callback.answer("Произошла ошибка при изменении стоимости", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("change_final:"))
async def handle_admin_change_final_price(callback: types.CallbackQuery):
    """Handle admin final price change request"""
    try:
        booking_id = callback.data.split(":")[1]
        admin_username = callback.from_user.username or str(callback.from_user.id)
        
        logger.info(f"Admin {admin_username} requested final price change for booking {booking_id}")
        
        # TODO: Implement final price change interface
        # This would typically show an inline form or ask for new final price
        
        await callback.answer(
            "💵 Функция изменения итоговой цены в разработке. Свяжитесь с разработчиком.",
            show_alert=True
        )
        
        # Send update notification to admin chat
        admin_service = AdminNotificationService(callback.bot, settings.admin_chat_id)
        await admin_service.notify_booking_updated(booking_id, "запрос изменения итоговой цены", admin_username)
        
    except Exception as e:
        logger.error(f"Error handling admin final price change: {e}")
        await callback.answer("Произошла ошибка при изменении цены", show_alert=True)


@router.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handler for all callback queries"""

    try:
        # Process callback based on data
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
