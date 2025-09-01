from typing import Optional
from pydantic import BaseModel, Field


class BookingExtract(BaseModel):
    TARIFF: Optional[str] = Field(
        None, description="Допустимо: '12 часов','1 сутки', ..."
    )
    FIRST_BEDROOM: Optional[bool] = None
    SECOND_BEDROOM: Optional[bool] = None
    SAUNA: Optional[bool] = None
    PHOTOSHOOT: Optional[bool] = None
    SECRET_ROOM: Optional[bool] = None
    START_DATE: Optional[str] = Field(None, description="ДД.ММ.ГГГГ")
    START_TIME: Optional[str] = Field(None, description="HH:MM 24h")
    FINISH_DATE: Optional[str] = Field(None, description="ДД.ММ.ГГГГ")
    FINISH_TIME: Optional[str] = Field(None, description="HH:MM 24h")
    NUMBER_GUESTS: Optional[int] = None
    CONTACT: Optional[str] = None
    COMMENT: Optional[str] = None
