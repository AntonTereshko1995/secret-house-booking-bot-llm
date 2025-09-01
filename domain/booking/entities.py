"""
Доменные сущности бронирования
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Booking(BaseModel):
    """Booking entity"""

    id: UUID = Field(default_factory=uuid4)
    user_id: int
    tariff: str
    start_date: datetime
    start_time: str
    finish_date: datetime
    finish_time: str
    first_bedroom: bool
    second_bedroom: bool
    sauna: bool
    photoshoot: bool
    secret_room: bool
    number_guests: int
    contact: str
    comment: str | None = None
    status: str = Field(default="pending")  # pending, confirmed, cancelled
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class BookingRequest(BaseModel):
    """Booking request"""

    user_id: int
    tariff: str
    start_date: datetime
    start_time: str
    finish_date: datetime
    finish_time: str
    first_bedroom: bool
    second_bedroom: bool
    sauna: bool
    photoshoot: bool
    secret_room: bool
    number_guests: int
    contact: str
    comment: str | None = None
