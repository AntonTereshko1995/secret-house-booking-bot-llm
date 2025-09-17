"""
Booking database model

SQLAlchemy model mapping exactly to the Booking domain entity.
Preserves all existing fields and relationships.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Numeric
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class BookingModel(BaseModel):
    """Booking model mapping to domain entity"""
    __tablename__ = "bookings"
    
    # User relationship - both UUID and direct Telegram ID for performance
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to user record"
    )
    
    telegram_user_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Direct Telegram user ID for quick lookups"
    )
    
    # Booking details - exact mapping to domain entity
    tariff = Column(
        String(100),
        nullable=False,
        comment="Booking tariff type"
    )
    
    start_date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Booking start date"
    )
    
    finish_date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Booking end date"
    )
    
    # Room and service selections
    white_bedroom = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="White bedroom (additional bedroom)"
    )
    
    green_bedroom = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Green bedroom (main bedroom)"
    )
    
    sauna = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Sauna service included"
    )
    
    photoshoot = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Photoshoot service included"
    )
    
    secret_room = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Secret room access included"
    )
    
    # Guest information
    number_guests = Column(
        Integer,
        nullable=False,
        comment="Number of guests"
    )
    
    comment = Column(
        Text,
        nullable=True,
        comment="Additional comments or requests"
    )
    
    # Pricing
    price = Column(
        Numeric(precision=10, scale=2),
        nullable=True,
        comment="Total booking price"
    )
    
    # Status management
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        comment="Booking status: pending, confirmed, cancelled"
    )
    
    payment_status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        comment="Payment status from PaymentStatus enum"
    )
    
    # Payment proof stored as JSON (PaymentProof model)
    payment_proof = Column(
        JSON,
        nullable=True,
        comment="Payment proof metadata as JSON"
    )
    
    # Audit and modification tracking
    modification_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times booking was modified"
    )
    
    last_modified_by = Column(
        Integer,
        nullable=True,
        comment="Telegram user ID of last modifier (admin)"
    )
    
    # Relationships
    user = relationship(
        "UserModel",
        back_populates="bookings",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<BookingModel(id={self.id}, telegram_user_id={self.telegram_user_id}, "
            f"tariff={self.tariff}, status={self.status})>"
        )