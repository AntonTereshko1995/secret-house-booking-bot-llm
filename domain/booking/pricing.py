"""
Доменные сущности ценообразования
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TariffRate(BaseModel):
    """Информация о тарифе на основе конфигурации из PRP"""

    tariff: int
    name: str
    duration_hours: int
    price: Decimal
    sauna_price: Decimal
    secret_room_price: Decimal
    second_bedroom_price: Decimal
    extra_hour_price: Decimal
    extra_people_price: Decimal
    photoshoot_price: Decimal
    max_people: int
    is_check_in_time_limit: bool
    is_photoshoot: bool
    is_transfer: bool
    subscription_type: int
    multi_day_prices: dict[str, Decimal] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class AddOnService(BaseModel):
    """Дополнительная услуга"""

    service_id: str
    name: str
    price: Decimal
    is_per_hour: bool = False
    description: str

    class Config:
        from_attributes = True


class PricingRequest(BaseModel):
    """Запрос на расчет стоимости"""

    tariff: str | None = None
    tariff_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    duration_hours: int | None = None
    duration_days: int | None = None
    add_ons: list[str] = Field(default_factory=list)  # Service IDs
    number_guests: int | None = None
    is_weekend: bool = False

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PricingBreakdown(BaseModel):
    """Детальная разбивка стоимости"""

    tariff_name: str
    tariff_id: int
    base_cost: Decimal
    duration_hours: int
    duration_days: int = 1
    add_on_costs: dict[str, Decimal] = Field(default_factory=dict)
    total_cost: Decimal
    currency: str = "RUB"
    max_people: int
    includes_transfer: bool = False
    includes_photoshoot: bool = False

    class Config:
        from_attributes = True


class PricingResponse(BaseModel):
    """Полный ответ по ценообразованию"""

    breakdown: PricingBreakdown
    formatted_message: str
    booking_suggestion: str
    valid_until: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
