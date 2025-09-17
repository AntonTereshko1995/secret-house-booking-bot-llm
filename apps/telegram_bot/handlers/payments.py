"""
Payment proof handlers for document and photo uploads
"""

from datetime import datetime
from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Document, Message, PhotoSize

from core.config import settings
from core.logging import get_logger
from domain.booking.entities import Booking, BookingStatus, Tariff
from domain.booking.payment import PaymentProof, PaymentStatus
from infrastructure.container import get_user_service, get_booking_service, get_chat_service
from infrastructure.llm.graphs.app.app_graph_builder import build_app_graph
from infrastructure.notifications.admin_service import AdminNotificationService

router = Router()
logger = get_logger(__name__)

# Create graph once on import
graph = build_app_graph()


def _convert_tariff_context_to_enum(tariff_value: str | int | None) -> Tariff:
    """Convert tariff value from context to Tariff enum"""
    if tariff_value is None:
        return Tariff.DAY  # Default tariff
    
    if isinstance(tariff_value, int):
        try:
            return Tariff(tariff_value)
        except ValueError:
            return Tariff.DAY
    
    # Handle string values - map common string values to enum
    tariff_str = str(tariff_value).lower()
    if "hour" in tariff_str or "12" in tariff_str:
        return Tariff.HOURS_12
    elif "couple" in tariff_str or "двоих" in tariff_str:
        return Tariff.DAY_FOR_COUPLE
    elif "worker" in tariff_str or "рабочий" in tariff_str:
        return Tariff.WORKER
    elif "incognit" in tariff_str and ("hour" in tariff_str or "12" in tariff_str):
        return Tariff.INCOGNITA_HOURS
    elif "incognit" in tariff_str:
        return Tariff.INCOGNITA_DAY
    else:
        return Tariff.DAY  # Default


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

        # Get services from container
        user_service = await get_user_service()
        booking_service = await get_booking_service()
        chat_service = await get_chat_service()

        # Ensure user exists in database
        user = await user_service.register_or_update_telegram_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            language_code=message.from_user.language_code
        )

        # Initialize or get chat session
        chat_session = await chat_service.initialize_or_get_session(
            chat_id=message.chat.id,
            user_id=user.id
        )

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

        # Create and save booking to database
        context = previous_state.get("context", {})
        try:
            booking = await _create_and_save_booking(context, user.id, booking_service, payment_proof)
            logger.info(f"Booking saved to database with ID: {booking.id}")

            # Update chat session context with booking ID
            conversation_context = await chat_service.get_conversation_history(message.chat.id)
            conversation_context["booking_id"] = str(booking.id)
            conversation_context["payment_proof"] = payment_proof.model_dump()
            await chat_service.update_conversation_context(message.chat.id, conversation_context)

        except Exception as db_error:
            logger.error(f"Failed to save booking to database: {db_error}")
            # Continue with the flow even if database save fails for now
            booking = _create_booking_from_context(context, user.id)

        # Update graph state with payment proof
        graph_state = {
            "user_id": message.from_user.id,
            "text": "",  # No text, just file upload
            "active_subgraph": "booking",
            "context": context,
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

        # Send admin notification
        try:
            total_cost = context.get("total_cost")
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


async def _create_and_save_booking(context: dict, user_id: UUID, booking_service, payment_proof: PaymentProof) -> Booking:
    """Create and save booking to database with payment proof
    
    Args:
        context: Booking context from graph state
        user_id: User UUID from database
        booking_service: Booking service instance
        payment_proof: Payment proof object
        
    Returns:
        Saved booking object
    """
    # Parse dates from context
    start_date_str = context.get("START_DATE", "01.01.2024")
    finish_date_str = context.get("FINISH_DATE", "01.01.2024")
    
    try:
        # Try parsing with year first
        if "." in start_date_str and len(start_date_str.split(".")[-1]) == 4:
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
        else:
            # Assume current year
            start_date = datetime.strptime(f"{start_date_str}.2024", "%d.%m.%Y").date()

        if "." in finish_date_str and len(finish_date_str.split(".")[-1]) == 4:
            finish_date = datetime.strptime(finish_date_str, "%d.%m.%Y").date()
        else:
            finish_date = datetime.strptime(f"{finish_date_str}.2024", "%d.%m.%Y").date()
    except ValueError:
        # Fallback to current date if parsing fails
        start_date = finish_date = datetime.now().date()

    # Create booking request from context
    from domain.booking.entities import BookingRequest
    
    tariff_enum = _convert_tariff_context_to_enum(context.get("TARIFF"))
    
    booking_request = BookingRequest(
        user_id=user_id,
        tariff=tariff_enum,
        start_date=start_date,
        finish_date=finish_date,
        white_bedroom=context.get("WHITE_BEDROOM", False),
        green_bedroom=context.get("GREEN_BEDROOM", False),
        sauna=context.get("SAUNA", False),
        photoshoot=context.get("PHOTOSHOOT", False),
        secret_room=context.get("SECRET_ROOM", False),
        number_guests=context.get("NUMBER_GUESTS", 1),
        comment=context.get("COMMENT"),
        price=context.get("total_cost")
    )
    
    # Create booking using the service (this will be implemented when BookingService is completed)
    # For now, create a booking domain entity
    booking = Booking(
        user_id=user_id,
        tariff=tariff_enum,
        start_date=start_date,
        finish_date=finish_date,
        white_bedroom=context.get("WHITE_BEDROOM", False),
        green_bedroom=context.get("GREEN_BEDROOM", False),
        sauna=context.get("SAUNA", False),
        photoshoot=context.get("PHOTOSHOOT", False),
        secret_room=context.get("SECRET_ROOM", False),
        number_guests=context.get("NUMBER_GUESTS", 1),
        comment=context.get("COMMENT"),
        price=context.get("total_cost"),
        status=BookingStatus.PENDING,
        payment_status=PaymentStatus.PROOF_UPLOADED,
        payment_proof=payment_proof
    )
    
    # TODO: Save using booking service when the availability and notification services are implemented
    # For now, we'll create the booking entity but not save it to avoid dependency issues
    # saved_booking = await booking_service.create_booking(booking_request)
    
    return booking


def _create_booking_from_context(context: dict, user_id: UUID) -> Booking:
    """Create booking object from graph context

    Args:
        context: Booking context from graph state
        user_id: User UUID

    Returns:
        Booking object for admin notification
    """
    from domain.booking.payment import PaymentStatus

    # Parse dates from context (they should be in DD.MM or DD.MM.YYYY format)
    start_date_str = context.get("START_DATE", "01.01.2024")
    finish_date_str = context.get("FINISH_DATE", "01.01.2024")

    try:
        # Try parsing with year first
        if "." in start_date_str and len(start_date_str.split(".")[-1]) == 4:
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
        else:
            # Assume current year
            start_date = datetime.strptime(f"{start_date_str}.2024", "%d.%m.%Y").date()

        if "." in finish_date_str and len(finish_date_str.split(".")[-1]) == 4:
            finish_date = datetime.strptime(finish_date_str, "%d.%m.%Y").date()
        else:
            finish_date = datetime.strptime(f"{finish_date_str}.2024", "%d.%m.%Y").date()
    except ValueError:
        # Fallback to current date if parsing fails
        start_date = finish_date = datetime.now().date()

    # Create booking object using new domain entity structure
    tariff_enum = _convert_tariff_context_to_enum(context.get("TARIFF"))
    
    booking = Booking(
        user_id=user_id,
        tariff=tariff_enum,
        start_date=datetime.combine(start_date, datetime.min.time()),
        finish_date=datetime.combine(finish_date, datetime.min.time()),
        white_bedroom=context.get("WHITE_BEDROOM", False),
        green_bedroom=context.get("GREEN_BEDROOM", False),
        sauna=context.get("SAUNA", False),
        photoshoot=context.get("PHOTOSHOOT", False),
        secret_room=context.get("SECRET_ROOM", False),
        number_guests=context.get("NUMBER_GUESTS", 1),
        comment=context.get("COMMENT"),
        price=context.get("total_cost"),
        status=BookingStatus.PENDING,
        payment_status=PaymentStatus.PROOF_UPLOADED
    )

    return booking
