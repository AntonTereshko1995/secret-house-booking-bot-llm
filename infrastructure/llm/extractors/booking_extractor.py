from datetime import datetime
from zoneinfo import ZoneInfo
from core.config import settings
from infrastructure.llm.clients.openai_client import get_llm
from infrastructure.llm.parsers.pydantic_factory import make_parser
from infrastructure.llm.prompts.extract_booking_promt import make_prompt
from infrastructure.llm.schemas.booking_extract_schema import BookingExtract

TZ = ZoneInfo(settings.timezone)

class BookingExtractor:
    def __init__(self):
        self.llm = get_llm()
        self.parser = make_parser(BookingExtract)

    async def aextract(self, text: str) -> dict:
        now = datetime.now(TZ)
        today = now.strftime("%d.%m.%Y")
        year = now.strftime("%Y")

        prompt = make_prompt(self.parser.get_format_instructions())
        msg = await prompt.ainvoke({"text": text, "TODAY": today, "YEAR": year})
        out = await self.llm.ainvoke(msg)
        data = self.parser.parse(out.content).model_dump(exclude_none=True)

        # Year insurance (if model didn't add year)
        for k in ("START_DATE", "FINISH_DATE"):
            if k in data and len(data[k]) == 5:   # DD.MM
                data[k] = f"{data[k]}.{year}"
        return data
