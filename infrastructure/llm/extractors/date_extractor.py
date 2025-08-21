from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Tuple, Optional
from core.config import settings
from infrastructure.llm.clients.openai_client import get_llm
from infrastructure.llm.parsers.pydantic_factory import make_parser
# from infrastructure.llm.prompts.extract_date_prompt import make_prompt
# from infrastructure.llm.schemas.date_extract_schema import DateExtract

TZ = ZoneInfo(settings.timezone)

class DateExtractor:
    def __init__(self):
        self.llm = get_llm()
        # self.parser = make_parser(DateExtract)

    # async def aextract(self, text: str) -> dict:
    #     now = datetime.now(TZ)
    #     today = now.strftime("%d.%m.%Y")
    #     year = now.strftime("%Y")

    #     prompt = make_prompt(self.parser.get_format_instructions())
    #     msg = await prompt.ainvoke({"text": text, "TODAY": today, "YEAR": year})
    #     out = await self.llm.ainvoke(msg)
    #     data = self.parser.parse(out.content).model_dump(exclude_none=True)
        
    #     return data

    def month_bounds_from_text(self, text: str) -> Tuple[datetime, datetime, str]:
        """
        Извлекает границы месяца из текста.
        Возвращает (начало_месяца, конец_месяца, метка_месяца)
        """
        now = datetime.now(TZ)
        
        # Простые паттерны для определения месяца
        text_lower = text.lower()
        
        # Текущий месяц
        if any(word in text_lower for word in ["текущий", "этот", "сейчас", "теперь"]):
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(seconds=1)
            else:
                month_end = now.replace(month=now.month + 1, day=1) - timedelta(seconds=1)
            return month_start, month_end, "текущий месяц"
        
        # Следующий месяц
        if any(word in text_lower for word in ["следующий", "будущий"]):
            if now.month == 12:
                month_start = now.replace(year=now.year + 1, month=1, day=1)
                month_end = now.replace(year=now.year + 1, month=2, day=1) - timedelta(seconds=1)
            else:
                month_start = now.replace(month=now.month + 1, day=1)
                month_end = now.replace(month=now.month + 2, day=1) - timedelta(seconds=1)
            return month_start, month_end, "следующий месяц"
        
        # Конкретные месяцы
        months = {
            "январь": 1, "февраль": 2, "март": 3, "апрель": 4,
            "май": 5, "июнь": 6, "июль": 7, "август": 8,
            "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12
        }
        
        for month_name, month_num in months.items():
            if month_name in text_lower:
                year = now.year
                # Если месяц уже прошел в этом году, берем следующий год
                if month_num < now.month:
                    year += 1
                
                month_start = datetime(year, month_num, 1, tzinfo=TZ)
                if month_num == 12:
                    month_end = datetime(year + 1, 1, 1, tzinfo=TZ) - timedelta(seconds=1)
                else:
                    month_end = datetime(year, month_num + 1, 1, tzinfo=TZ) - timedelta(seconds=1)
                
                return month_start, month_end, month_name
        
        # По умолчанию - текущий месяц
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            month_end = now.replace(month=now.month + 1, day=1) - timedelta(seconds=1)
        
        return month_start, month_end, "текущий месяц"
