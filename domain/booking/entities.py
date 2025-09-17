from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from .payment import PaymentStatus, PaymentProof


class Tariff(int, Enum):
    """Tariff enumeration for booking rates"""
    HOURS_12 = 0
    DAY = 1
    WORKER = 2
    INCOGNITA_DAY = 3
    INCOGNITA_HOURS = 4
    DAY_FOR_COUPLE = 5


class BookingStatus(str, Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(BaseModel):
    """Booking entity"""

    id: UUID = Field(default_factory=uuid4)
    user_id: int
    tariff: Tariff
    start_date: datetime
    finish_date: datetime
    white_bedroom: bool
    green_bedroom: bool
    sauna: bool
    photoshoot: bool
    secret_room: bool
    number_guests: int
    comment: str | None = None
    price: Optional[Decimal] = Field(None, description="Total booking price", ge=0)
    status: BookingStatus = Field(default=BookingStatus.PENDING, description="Booking status")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    payment_proof: Optional[PaymentProof] = Field(None, description="Payment proof document/photo")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class BookingRequest(BaseModel):
    """Booking request"""

    user_id: int
    tariff: Tariff
    start_date: datetime
    finish_date: datetime
    white_bedroom: bool
    green_bedroom: bool
    sauna: bool
    photoshoot: bool
    secret_room: bool
    number_guests: int
    comment: str | None = None
    price: Optional[Decimal] = Field(None, description="Total booking price", ge=0)
