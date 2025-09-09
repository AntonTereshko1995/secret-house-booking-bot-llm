"""
Payment proof handlers for document and photo uploads
"""

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Document, Message, PhotoSize

from core.config import settings
from core.logging import get_logger
from domain.booking.entities import Booking
from domain.booking.payment import PaymentProof, PaymentStatus
from infrastructure.llm.graphs.app.app_graph_builder import build_app_graph
from infrastructure.notifications.admin_service import AdminNotificationService

router = Router()
logger = get_logger(__name__)

# Create graph once on import
graph = build_app_graph()


async def process_payment_proof(
    message: Message,
    state: FSMContext,
    file_id: str,
    file_type: str,
    file_size: int = None,
) -> None:
    """Process payment proof upload (document or photo)

    Args:
        message: Telegram message with file
        state: FSM context
        file_id: Telegram file ID
        file_type: File type (document or photo)
        file_size: File size in bytes (optional)
    """
    thread_id = f"{message.chat.id}:{message.from_user.id}"

    try:
        # Get previous state from graph
        checkpoint = await graph.aget_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        previous_state = checkpoint.values if checkpoint else {}

        # Check if user is in payment flow
        payment_status = previous_state.get("payment_status")
        if payment_status != PaymentStatus.PENDING.value:
            await message.answer(
                "Сначала подтвердите детали бронирования, затем загружайте подтверждение оплаты."
            )
            return

        # Create payment proof object
        payment_proof = PaymentProof(
            file_id=file_id,
            file_type=file_type,
            file_size=file_size,
            uploaded_at=datetime.now(),
            user_id=message.from_user.id,
        )

        logger.info(
            f"Payment proof uploaded by user {message.from_user.id}: {file_type}, size: {file_size}"
        )

        # Update graph state with payment proof
        graph_state = {
            "user_id": message.from_user.id,
            "text": "",  # No text, just file upload
            "active_subgraph": "booking",
            "context": previous_state.get("context", {}),
            "payment_status": PaymentStatus.PROOF_UPLOADED.value,
            "payment_proof": payment_proof.model_dump(),
            "done": previous_state.get("done", False),
        }

        # Process through graph
        result = await graph.ainvoke(
            graph_state, config={"configurable": {"thread_id": thread_id}}
        )

        logger.info(f"Graph result for payment proof {thread_id}: {result}")

        # Send response to user
        reply = result.get(
            "reply",
            "Подтверждение оплаты получено, ожидается проверка администратором.",
        )
        await message.answer(reply)

        # Create booking object from context for admin notification
        context = previous_state.get("context", {})
        try:
            booking = _create_booking_from_context(context, message.from_user.id)
            total_cost = context.get("total_cost")

            # Initialize admin service and send notification
            bot = message.bot
            admin_service = AdminNotificationService(bot, settings.admin_chat_id)
            await admin_service.notify_new_booking(booking, payment_proof, total_cost)

            logger.info(f"Admin notification sent for booking {booking.id}")

        except Exception as admin_error:
            logger.error(f"Failed to send admin notification: {admin_error}")
            # Don't fail the user flow if admin notification fails

    except Exception as e:
        logger.error(f"Error processing payment proof for {thread_id}: {e}")
        await message.answer(
            "Произошла ошибка при обработке подтверждения оплаты. Попробуйте позже."
        )


@router.message(F.document)
async def handle_payment_document(message: Message, state: FSMContext):
    """Handle document upload as payment proof"""
    document: Document = message.document

    logger.info(
        f"Document uploaded by user {message.from_user.id}: {document.file_name}, size: {document.file_size}"
    )

    # Check file size limit (20MB for Telegram Bot API)
    if document.file_size and document.file_size > 20 * 1024 * 1024:
        await message.answer("Файл слишком большой. Максимальный размер: 20 МБ.")
        return

    await process_payment_proof(
        message=message,
        state=state,
        file_id=document.file_id,
        file_type="document",
        file_size=document.file_size,
    )


@router.message(F.photo)
async def handle_payment_photo(message: Message, state: FSMContext):
    """Handle photo upload as payment proof"""
    # Get the largest photo size
    photo: PhotoSize = message.photo[-1]

    logger.info(
        f"Photo uploaded by user {message.from_user.id}: size: {photo.file_size}"
    )

    await process_payment_proof(
        message=message,
        state=state,
        file_id=photo.file_id,
        file_type="photo",
        file_size=photo.file_size,
    )


def _create_booking_from_context(context: dict, user_id: int) -> Booking:
    """Create booking object from graph context

    Args:
        context: Booking context from graph state
        user_id: User ID

    Returns:
        Booking object for admin notification
    """
    from datetime import datetime

    from domain.booking.payment import PaymentStatus

    # Parse dates from context (they should be in DD.MM or DD.MM.YYYY format)
    start_date_str = context.get("START_DATE", "01.01.2024")
    finish_date_str = context.get("FINISH_DATE", "01.01.2024")

    try:
        # Try parsing with year first
        if "." in start_date_str and len(start_date_str.split(".")[-1]) == 4:
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
        else:
            # Assume current year
            start_date = datetime.strptime(f"{start_date_str}.2024", "%d.%m.%Y")

        if "." in finish_date_str and len(finish_date_str.split(".")[-1]) == 4:
            finish_date = datetime.strptime(finish_date_str, "%d.%m.%Y")
        else:
            finish_date = datetime.strptime(f"{finish_date_str}.2024", "%d.%m.%Y")
    except ValueError:
        # Fallback to current date if parsing fails
        start_date = finish_date = datetime.now()

    # Create booking object
    booking = Booking(
        user_id=user_id,
        tariff=str(context.get("TARIFF", "unknown")),
        start_date=start_date,
        start_time=context.get("START_TIME", "14:00"),
        finish_date=finish_date,
        finish_time=context.get("FINISH_TIME", "12:00"),
        first_bedroom=context.get("FIRST_BEDROOM", False),
        second_bedroom=context.get("SECOND_BEDROOM", False),
        sauna=context.get("SAUNA", False),
        photoshoot=context.get("PHOTOSHOOT", False),
        secret_room=context.get("SECRET_ROOM", False),
        number_guests=context.get("NUMBER_GUESTS", 1),
        contact=context.get("CONTACT", "unknown"),
        comment=context.get("COMMENT"),
        payment_status=PaymentStatus.PROOF_UPLOADED,
        status="pending",
    )

    return booking
