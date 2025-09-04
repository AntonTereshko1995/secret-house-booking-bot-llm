from pydantic import BaseModel, Field


class BookingExtract(BaseModel):
    TARIFF: str | None = Field(None, description="Допустимо: '12 часов','1 сутки', ...")
    FIRST_BEDROOM: bool | None = None
    SECOND_BEDROOM: bool | None = None
    SAUNA: bool | None = None
    PHOTOSHOOT: bool | None = None
    SECRET_ROOM: bool | None = None
    START_DATE: str | None = Field(None, description="ДД.ММ.ГГГГ")
    START_TIME: str | None = Field(None, description="HH:MM 24h")
    FINISH_DATE: str | None = Field(None, description="ДД.ММ.ГГГГ")
    FINISH_TIME: str | None = Field(None, description="HH:MM 24h")
    NUMBER_GUESTS: int | None = None
    CONTACT: str | None = None
    COMMENT: str | None = None
