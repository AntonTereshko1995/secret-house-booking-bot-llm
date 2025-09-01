"""
Доменные сущности доступности
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class AvailabilitySlot(BaseModel):
    """Слот доступности для конкретной даты"""

    date: datetime
    is_available: bool
    booking_id: Optional[UUID] = None
    price: Optional[Decimal] = None

    class Config:
        from_attributes = True


class AvailabilityPeriod(BaseModel):
    """Период доступности с множественными слотами"""

    start_date: datetime
    end_date: datetime
    slots: List[AvailabilitySlot]
    total_available_days: int = Field(ge=0)

    class Config:
        from_attributes = True


class AvailabilityRequest(BaseModel):
    """Запрос на проверку доступности"""

    start_date: datetime
    end_date: datetime
    user_timezone: str = Field(default="Europe/Minsk")

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    """Ответ с информацией о доступности"""

    period: AvailabilityPeriod
    message: str
    suggestions: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
