"""
Admin notification service for booking management
"""

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.logging import get_logger
from domain.booking.entities import Booking
from domain.booking.payment import PaymentProof
from infrastructure.llm.graphs.booking.booking_graph import (
    Tariff,
    get_rate_display_name,
)

logger = get_logger(__name__)


class AdminNotificationService:
    """Service for sending admin notifications with action buttons"""

    def __init__(self, bot: Bot, admin_chat_id: int):
        """Initialize admin notification service

        Args:
            bot: Aiogram Bot instance
            admin_chat_id: Admin chat ID for notifications
        """
        self.bot = bot
        self.admin_chat_id = admin_chat_id

    async def notify_new_booking(
        self, booking: Booking, payment_proof: PaymentProof, total_cost: float = None
    ) -> None:
        """Send new booking notification to admin chat

        Args:
            booking: Booking entity
            payment_proof: Payment proof document/photo
            total_cost: Calculated total cost (optional)
        """
        try:
            # Build booking summary message
            message = self._build_booking_summary(booking, payment_proof, total_cost)

            # Create admin action keyboard
            keyboard = self._build_admin_keyboard(str(booking.id))

            # Send notification to admin chat
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

            logger.info(f"Sent admin notification for booking {booking.id}")

        except Exception as e:
            logger.error(
                f"Failed to send admin notification for booking {booking.id}: {e}"
            )
            raise

    def _build_booking_summary(
        self, booking: Booking, payment_proof: PaymentProof, total_cost: float = None
    ) -> str:
        """Build booking summary message for admin

        Args:
            booking: Booking entity
            payment_proof: Payment proof document/photo
            total_cost: Calculated total cost (optional)

        Returns:
            Formatted booking summary message
        """
        # Get tariff display name
        tariff_display = "Неизвестно"
        if booking.tariff.isdigit():
            try:
                tariff_enum = Tariff(int(booking.tariff))
                tariff_display = get_rate_display_name(tariff_enum)
            except (ValueError, KeyError):
                tariff_display = booking.tariff
        else:
            tariff_display = booking.tariff

        # Format dates and times
        start_date = booking.start_date.strftime("%d.%m.%Y")
        finish_date = booking.finish_date.strftime("%d.%m.%Y")

        # Build message components
        message_parts = [
            "🏠 <b>НОВОЕ БРОНИРОВАНИЕ</b>",
            "",
            f"📅 <b>Заезд:</b> {start_date} в {booking.start_time}",
            f"📅 <b>Выезд:</b> {finish_date} в {booking.finish_time}",
            f"🎯 <b>Тариф:</b> {tariff_display}",
            f"👥 <b>Гостей:</b> {booking.number_guests}",
        ]

        # Add optional services
        services = []
        if booking.first_bedroom:
            services.append("1-я спальня")
        if booking.second_bedroom:
            services.append("2-я спальня")
        if booking.sauna:
            services.append("Сауна")
        if booking.photoshoot:
            services.append("Фотосъёмка")
        if booking.secret_room:
            services.append("Секретная комната")

        if services:
            message_parts.append(f"🔧 <b>Услуги:</b> {', '.join(services)}")

        # Add contact and cost info
        message_parts.extend(
            [
                f"📱 <b>Контакт:</b> {booking.contact}",
                f"💰 <b>Стоимость:</b> {total_cost or 'Рассчитывается'} BYN",
            ]
        )

        # Add comment if present
        if booking.comment:
            message_parts.append(f"💬 <b>Комментарий:</b> {booking.comment}")

        # Add payment proof info
        proof_type = (
            "📄 Документ" if payment_proof.file_type == "document" else "📸 Фото"
        )
        upload_time = payment_proof.uploaded_at.strftime("%d.%m.%Y %H:%M")
        message_parts.extend(
            [
                "",
                f"💳 <b>Подтверждение оплаты:</b> {proof_type}",
                f"⏰ <b>Загружено:</b> {upload_time}",
                f"👤 <b>User ID:</b> {booking.user_id}",
                f"🆔 <b>Booking ID:</b> {booking.id}",
            ]
        )

        return "\n".join(message_parts)

    def _build_admin_keyboard(self, booking_id: str) -> InlineKeyboardMarkup:
        """Build inline keyboard for admin actions

        Args:
            booking_id: Booking ID for callback data

        Returns:
            InlineKeyboardMarkup with admin action buttons
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Подтвердить", callback_data=f"approve:{booking_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Отменить", callback_data=f"cancel:{booking_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💰 Изменить стоимость",
                        callback_data=f"change_cost:{booking_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💵 Изменить итог",
                        callback_data=f"change_final:{booking_id}",
                    )
                ],
            ]
        )

        return keyboard

    async def notify_booking_updated(
        self, booking_id: str, action: str, admin_username: str = None
    ) -> None:
        """Send booking update notification

        Args:
            booking_id: Booking ID
            action: Action taken (approved, cancelled, etc.)
            admin_username: Admin who performed the action
        """
        try:
            admin_info = f" (by @{admin_username})" if admin_username else ""
            message = f"📋 Бронирование {booking_id} - {action.upper()}{admin_info}"

            await self.bot.send_message(chat_id=self.admin_chat_id, text=message)

            logger.info(f"Sent booking update notification: {booking_id} - {action}")

        except Exception as e:
            logger.error(f"Failed to send booking update notification: {e}")
            # Don't raise here as this is a secondary notification
