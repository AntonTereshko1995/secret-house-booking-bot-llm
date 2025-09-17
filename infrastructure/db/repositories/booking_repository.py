"""
Booking repository implementation

Repository for booking-specific database operations including
booking creation, modification, and audit tracking.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from domain.booking.entities import Booking, BookingRequest
from domain.booking.payment import PaymentStatus
from infrastructure.db.models.booking import BookingModel

from .base import BaseRepository

logger = get_logger(__name__)


class BookingRepository(BaseRepository[Booking, BookingModel]):
    """Booking repository for booking management"""
    
    def __init__(self, session: AsyncSession):
        """Initialize booking repository
        
        Args:
            session: Async SQLAlchemy session
        """
        super().__init__(session, BookingModel)
    
    async def find_by_telegram_user_id(self, telegram_user_id: int) -> List[BookingModel]:
        """Find all bookings for a Telegram user
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            List of booking model instances
        """
        try:
            stmt = (
                select(BookingModel)
                .where(BookingModel.telegram_user_id == telegram_user_id)
                .order_by(BookingModel.created_at.desc())
            )
            result = await self.session.execute(stmt)
            bookings = list(result.scalars().all())
            
            logger.debug(
                "Found bookings for user",
                extra={"telegram_user_id": telegram_user_id, "count": len(bookings)}
            )
            
            return bookings
            
        except Exception as e:
            logger.error(
                f"Error finding bookings by Telegram user ID: {e}",
                extra={"telegram_user_id": telegram_user_id}
            )
            raise
    
    async def find_by_status(self, status: str) -> List[BookingModel]:
        """Find bookings by status
        
        Args:
            status: Booking status (pending, confirmed, cancelled)
            
        Returns:
            List of booking model instances
        """
        try:
            stmt = (
                select(BookingModel)
                .where(BookingModel.status == status)
                .order_by(BookingModel.created_at.desc())
            )
            result = await self.session.execute(stmt)
            bookings = list(result.scalars().all())
            
            logger.debug(
                "Found bookings by status",
                extra={"status": status, "count": len(bookings)}
            )
            
            return bookings
            
        except Exception as e:
            logger.error(
                f"Error finding bookings by status: {e}",
                extra={"status": status}
            )
            raise
    
    async def create_booking_from_request(
        self, 
        booking_request: BookingRequest,
        user_id: UUID,
        telegram_user_id: int
    ) -> BookingModel:
        """Create booking from domain request
        
        Args:
            booking_request: Booking request domain object
            user_id: User UUID from database
            telegram_user_id: Telegram user ID
            
        Returns:
            Created booking model instance
        """
        try:
            booking_data = {
                "user_id": user_id,
                "telegram_user_id": telegram_user_id,
                "tariff": booking_request.tariff,
                "start_date": booking_request.start_date,
                "start_time": booking_request.start_time,
                "finish_date": booking_request.finish_date,
                "finish_time": booking_request.finish_time,
                "first_bedroom": booking_request.first_bedroom,
                "second_bedroom": booking_request.second_bedroom,
                "sauna": booking_request.sauna,
                "photoshoot": booking_request.photoshoot,
                "secret_room": booking_request.secret_room,
                "number_guests": booking_request.number_guests,
                "comment": booking_request.comment,
                "status": "pending",
                "payment_status": PaymentStatus.PENDING.value,
                "modification_count": 0
            }
            
            booking = await self.create(booking_data)
            
            logger.info(
                "Created booking from request",
                extra={
                    "booking_id": str(booking.id),
                    "telegram_user_id": telegram_user_id,
                    "tariff": booking_request.tariff
                }
            )
            
            return booking
            
        except Exception as e:
            logger.error(
                f"Error creating booking from request: {e}",
                extra={"telegram_user_id": telegram_user_id}
            )
            raise
    
    async def modify_booking_level(
        self, 
        booking_id: UUID, 
        new_tariff: str,
        modified_by: int
    ) -> Optional[BookingModel]:
        """Modify booking tariff level with audit tracking
        
        Args:
            booking_id: Booking UUID
            new_tariff: New tariff type
            modified_by: Telegram user ID of modifier
            
        Returns:
            Modified booking model instance or None if not found
        """
        try:
            # Get current booking
            booking = await self.find_by_id(booking_id)
            if not booking:
                logger.warning(
                    "Booking not found for level modification",
                    extra={"booking_id": str(booking_id)}
                )
                return None
            
            # Update booking with new level and audit info
            update_data = {
                "tariff": new_tariff,
                "modification_count": booking.modification_count + 1,
                "last_modified_by": modified_by,
                "updated_at": datetime.now()
            }
            
            stmt = (
                update(BookingModel)
                .where(BookingModel.id == booking_id)
                .values(**update_data)
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Fetch updated booking
            updated_booking = await self.find_by_id(booking_id)
            
            logger.info(
                "Modified booking level",
                extra={
                    "booking_id": str(booking_id),
                    "old_tariff": booking.tariff,
                    "new_tariff": new_tariff,
                    "modified_by": modified_by,
                    "modification_count": booking.modification_count + 1
                }
            )
            
            return updated_booking
            
        except Exception as e:
            logger.error(
                f"Error modifying booking level: {e}",
                extra={
                    "booking_id": str(booking_id),
                    "new_tariff": new_tariff,
                    "modified_by": modified_by
                }
            )
            raise
    
    async def update_payment_status(
        self, 
        booking_id: UUID, 
        payment_status: PaymentStatus,
        payment_proof: Optional[dict] = None
    ) -> Optional[BookingModel]:
        """Update booking payment status and proof
        
        Args:
            booking_id: Booking UUID
            payment_status: New payment status
            payment_proof: Optional payment proof data
            
        Returns:
            Updated booking model instance or None if not found
        """
        try:
            update_data = {
                "payment_status": payment_status.value,
                "updated_at": datetime.now()
            }
            
            if payment_proof:
                update_data["payment_proof"] = payment_proof
            
            updated_booking = await self.update(booking_id, update_data)
            
            if updated_booking:
                logger.info(
                    "Updated booking payment status",
                    extra={
                        "booking_id": str(booking_id),
                        "payment_status": payment_status.value,
                        "has_proof": payment_proof is not None
                    }
                )
            
            return updated_booking
            
        except Exception as e:
            logger.error(
                f"Error updating payment status: {e}",
                extra={
                    "booking_id": str(booking_id),
                    "payment_status": payment_status.value
                }
            )
            raise
    
    async def update_booking_status(
        self, 
        booking_id: UUID, 
        status: str,
        modified_by: Optional[int] = None
    ) -> Optional[BookingModel]:
        """Update booking status
        
        Args:
            booking_id: Booking UUID
            status: New booking status
            modified_by: Optional Telegram user ID of modifier
            
        Returns:
            Updated booking model instance or None if not found
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            if modified_by:
                update_data["last_modified_by"] = modified_by
            
            updated_booking = await self.update(booking_id, update_data)
            
            if updated_booking:
                logger.info(
                    "Updated booking status",
                    extra={
                        "booking_id": str(booking_id),
                        "status": status,
                        "modified_by": modified_by
                    }
                )
            
            return updated_booking
            
        except Exception as e:
            logger.error(
                f"Error updating booking status: {e}",
                extra={"booking_id": str(booking_id), "status": status}
            )
            raise
    
    def _to_domain_entity(self, db_booking: BookingModel) -> Booking:
        """Convert database model to domain entity
        
        Args:
            db_booking: Database booking model
            
        Returns:
            Booking domain entity
        """
        # Convert payment_proof JSON back to PaymentProof object if present
        payment_proof = None
        if db_booking.payment_proof:
            from domain.booking.payment import PaymentProof
            payment_proof = PaymentProof(**db_booking.payment_proof)
        
        return Booking(
            id=db_booking.id,
            user_id=db_booking.telegram_user_id,  # Map to Telegram ID for compatibility
            tariff=db_booking.tariff,
            start_date=db_booking.start_date,
            start_time=db_booking.start_time,
            finish_date=db_booking.finish_date,
            finish_time=db_booking.finish_time,
            first_bedroom=db_booking.first_bedroom,
            second_bedroom=db_booking.second_bedroom,
            sauna=db_booking.sauna,
            photoshoot=db_booking.photoshoot,
            secret_room=db_booking.secret_room,
            number_guests=db_booking.number_guests,
            comment=db_booking.comment,
            status=db_booking.status,
            payment_status=PaymentStatus(db_booking.payment_status),
            payment_proof=payment_proof,
            created_at=db_booking.created_at,
            updated_at=db_booking.updated_at
        )