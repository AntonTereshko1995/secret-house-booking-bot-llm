import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Tuple, Optional, List
from core.config import settings
from core.logging import get_logger
from infrastructure.llm.clients.openai_client import get_llm
from infrastructure.llm.parsers.pydantic_factory import make_parser

# from infrastructure.llm.prompts.extract_date_prompt import make_prompt
# from infrastructure.llm.schemas.date_extract_schema import DateExtract

TZ = ZoneInfo(settings.timezone)
logger = get_logger(__name__)


class DateExtractor:
    def __init__(self):
        self.llm = get_llm()
        # self.parser = make_parser(DateExtract)

        # Словари месяцев для парсинга дат
        self.russian_months = {
            "январь": 1,
            "января": 1,
            "янв": 1,
            "февраль": 2,
            "февраля": 2,
            "фев": 2,
            "март": 3,
            "марта": 3,
            "мар": 3,
            "апрель": 4,
            "апреля": 4,
            "апр": 4,
            "май": 5,
            "мая": 5,
            "июнь": 6,
            "июня": 6,
            "июн": 6,
            "июль": 7,
            "июля": 7,
            "июл": 7,
            "август": 8,
            "августа": 8,
            "авг": 8,
            "сентябрь": 9,
            "сентября": 9,
            "сен": 9,
            "сент": 9,
            "октябрь": 10,
            "октября": 10,
            "окт": 10,
            "ноябрь": 11,
            "ноября": 11,
            "ноя": 11,
            "декабрь": 12,
            "декабря": 12,
            "дек": 12,
        }

        self.english_months = {
            "january": 1,
            "jan": 1,
            "february": 2,
            "feb": 2,
            "march": 3,
            "mar": 3,
            "april": 4,
            "apr": 4,
            "may": 5,
            "june": 6,
            "jun": 6,
            "july": 7,
            "jul": 7,
            "august": 8,
            "aug": 8,
            "september": 9,
            "sep": 9,
            "sept": 9,
            "october": 10,
            "oct": 10,
            "november": 11,
            "nov": 11,
            "december": 12,
            "dec": 12,
        }
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
        Extracts month boundaries from text.
        Returns (month_start, month_end, month_label)
        """
        now = datetime.now(TZ)

        # Simple patterns for month detection
        text_lower = text.lower()

        # Current month
        if any(
            word in text_lower
            for word in [
                "текущий",
                "этот",
                "сейчас",
                "теперь",
                "current",
                "this",
                "now",
            ]
        ):
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(
                    seconds=1
                )
            else:
                month_end = now.replace(month=now.month + 1, day=1) - timedelta(
                    seconds=1
                )
            return month_start, month_end, "current month"

        # Next month
        if any(
            word in text_lower for word in ["следующий", "будущий", "next", "future"]
        ):
            if now.month == 12:
                month_start = now.replace(year=now.year + 1, month=1, day=1)
                month_end = now.replace(year=now.year + 1, month=2, day=1) - timedelta(
                    seconds=1
                )
            else:
                month_start = now.replace(month=now.month + 1, day=1)
                month_end = now.replace(month=now.month + 2, day=1) - timedelta(
                    seconds=1
                )
            return month_start, month_end, "next month"

        # Specific months
        months = {
            "январь": 1,
            "февраль": 2,
            "март": 3,
            "апрель": 4,
            "май": 5,
            "июнь": 6,
            "июль": 7,
            "август": 8,
            "сентябрь": 9,
            "октябрь": 10,
            "ноябрь": 11,
            "декабрь": 12,
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        for month_name, month_num in months.items():
            if month_name in text_lower:
                year = now.year
                # If month has already passed this year, take next year
                if month_num < now.month:
                    year += 1

                month_start = datetime(year, month_num, 1, tzinfo=TZ)
                if month_num == 12:
                    month_end = datetime(year + 1, 1, 1, tzinfo=TZ) - timedelta(
                        seconds=1
                    )
                else:
                    month_end = datetime(year, month_num + 1, 1, tzinfo=TZ) - timedelta(
                        seconds=1
                    )

                return month_start, month_end, month_name

        # Default - current month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(
                seconds=1
            )
        else:
            month_end = now.replace(month=now.month + 1, day=1) - timedelta(seconds=1)

        return month_start, month_end, "current month"

    def extract_specific_date(self, text: str) -> Optional[Tuple[datetime, str]]:
        """
        Извлекает конкретную дату из текста.
        Возвращает (date, matched_text) или None если не найдено
        """
        now = datetime.now(TZ)
        text_lower = text.lower()

        # Словарь месяцев
        months = {
            "январь": 1,
            "января": 1,
            "февраль": 2,
            "февраля": 2,
            "март": 3,
            "марта": 3,
            "апрель": 4,
            "апреля": 4,
            "май": 5,
            "мая": 5,
            "июнь": 6,
            "июня": 6,
            "июль": 7,
            "июля": 7,
            "август": 8,
            "августа": 8,
            "сентябрь": 9,
            "сентября": 9,
            "октябрь": 10,
            "октября": 10,
            "ноябрь": 11,
            "ноября": 11,
            "декабрь": 12,
            "декабря": 12,
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        # Паттерны для поиска дат: "15 марта", "March 20", "20.03", "2025-03-25" (ISO format)
        patterns = [
            # Приоритет: сначала ISO формат YYYY-MM-DD
            r"(\d{4})-(\d{1,2})-(\d{1,2})",
            # Затем остальные форматы
            r"(\d{1,2})\s+(январь|января|февраль|февраля|март|марта|апрель|апреля|май|мая|июнь|июня|июль|июля|август|августа|сентябрь|сентября|октябрь|октября|ноябрь|ноября|декабрь|декабря)",
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})",
            r"(\d{1,2})\.(0?\d{1,2})\.?(\d{2,4})?",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    match = matches[0]
                    if (
                        len(match) == 3
                        and match[0].isdigit()
                        and match[1].isdigit()
                        and match[2].isdigit()
                    ):
                        # Формат ISO "2025-03-25" (YYYY-MM-DD)
                        year = int(match[0])
                        month = int(match[1])
                        day = int(match[2])

                        if 1 <= month <= 12 and 1 <= day <= 31 and year >= 2000:
                            target_date = datetime(year, month, day, tzinfo=TZ)
                            return target_date, f"{year}-{month:02d}-{day:02d}"

                    elif (
                        len(match) == 2
                        and isinstance(match[0], str)
                        and match[0].isdigit()
                    ):
                        # Формат "15 марта"
                        day = int(match[0])
                        month_name = match[1]
                        month = months.get(month_name)
                        if month:
                            year = now.year
                            # Если дата уже прошла в этом году, берём следующий год
                            target_date = datetime(year, month, day, tzinfo=TZ)
                            if target_date.date() < now.date():
                                target_date = target_date.replace(year=year + 1)
                            return target_date, f"{day} {month_name}"

                    elif (
                        len(match) == 2
                        and isinstance(match[1], str)
                        and match[1].isdigit()
                    ):
                        # Формат "March 20"
                        month_name = match[0]
                        day = int(match[1])
                        month = months.get(month_name)
                        if month:
                            year = now.year
                            target_date = datetime(year, month, day, tzinfo=TZ)
                            if target_date.date() < now.date():
                                target_date = target_date.replace(year=year + 1)
                            return target_date, f"{month_name} {day}"

                    elif len(match) >= 2:
                        # Формат "20.03" или "20.03.2025"
                        day = int(match[0])
                        month = int(match[1])
                        year = (
                            now.year
                            if len(match) < 3 or not match[2]
                            else int(match[2])
                        )

                        if year < 100:  # Двухзначный год
                            year += 2000

                        if 1 <= month <= 12 and 1 <= day <= 31:
                            target_date = datetime(year, month, day, tzinfo=TZ)
                            if target_date.date() < now.date() and len(match) < 3:
                                target_date = target_date.replace(year=year + 1)
                            return target_date, f"{day:02d}.{month:02d}"
                except (ValueError, TypeError) as e:
                    logger.debug(f"Error parsing date: {e}")
                    continue

        return None

    def extract_date_range(self, text: str) -> Optional[Tuple[datetime, datetime, str]]:
        """
        Извлекает диапазон дат из текста различных форматов.
        Поддерживает русский, английский и цифровой форматы, включая ISO даты.

        Возвращает (start_date, end_date, matched_text) или None
        """
        text = text.lower().strip()

        # Паттерны для диапазонов: ISO format, "15-20 марта", "March 15-20", "15.03-20.03"
        patterns = [
            # Приоритет: ISO формат "2025-03-20 to 2025-03-25" или "2025-03-20 - 2025-03-25"
            r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(?:to|-|до|по)\s+(\d{4})-(\d{1,2})-(\d{1,2})",
            # Русский формат: "15-20 марта"
            r"(\d{1,2})\s*[-—]\s*(\d{1,2})\s+("
            + "|".join(self.russian_months.keys())
            + r")",
            # Английский формат: "march 15-20"
            r"("
            + "|".join(self.english_months.keys())
            + r")\s+(\d{1,2})\s*[-—]\s*(\d{1,2})",
            # Цифровой формат: "15.03-20.03"
            r"(\d{1,2})\.(\d{1,2})\s*[-—]\s*(\d{1,2})\.(\d{1,2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()

                try:
                    # ISO формат: 6 групп (год1, месяц1, день1, год2, месяц2, день2)
                    if len(groups) == 6:
                        year1, month1, day1, year2, month2, day2 = groups
                        start_date = datetime(
                            int(year1), int(month1), int(day1), tzinfo=TZ
                        )
                        end_date = datetime(
                            int(year2), int(month2), int(day2), 23, 59, 59, tzinfo=TZ
                        )

                        if self.validate_date_range(start_date, end_date):
                            return start_date, end_date, match.group()

                    # Русский формат: "15-20 марта" (3 группы: день1, день2, месяц)
                    elif len(groups) == 3 and groups[2] in self.russian_months:
                        start_day = int(groups[0])
                        end_day = int(groups[1])
                        month_name = groups[2]

                        if start_day > end_day:
                            continue

                        month = self.russian_months[month_name]
                        year = self._get_target_year_for_month(month)

                        start_date = datetime(year, month, start_day, tzinfo=TZ)
                        end_date = datetime(year, month, end_day, 23, 59, 59, tzinfo=TZ)

                        if self.validate_date_range(start_date, end_date):
                            return start_date, end_date, match.group()

                    # Английский формат: "march 15-20" (3 группы: месяц, день1, день2)
                    elif len(groups) == 3 and groups[0] in self.english_months:
                        month_name = groups[0]
                        start_day = int(groups[1])
                        end_day = int(groups[2])

                        if start_day > end_day:
                            continue

                        month = self.english_months[month_name]
                        year = self._get_target_year_for_month(month)

                        start_date = datetime(year, month, start_day, tzinfo=TZ)
                        end_date = datetime(year, month, end_day, 23, 59, 59, tzinfo=TZ)

                        if self.validate_date_range(start_date, end_date):
                            return start_date, end_date, match.group()

                    # Цифровой формат: "15.03-20.03" (4 группы: день1, месяц1, день2, месяц2)
                    elif len(groups) == 4:
                        start_day = int(groups[0])
                        start_month = int(groups[1])
                        end_day = int(groups[2])
                        end_month = int(groups[3])

                        # Определяем год для каждой даты
                        start_year = self._get_target_year_for_month(start_month)
                        end_year = self._get_target_year_for_month(end_month)

                        # Если конечный месяц меньше начального, вероятно это следующий год
                        if end_month < start_month:
                            end_year = start_year + 1

                        start_date = datetime(
                            start_year, start_month, start_day, tzinfo=TZ
                        )
                        end_date = datetime(
                            end_year, end_month, end_day, 23, 59, 59, tzinfo=TZ
                        )

                        if self.validate_date_range(start_date, end_date):
                            return start_date, end_date, match.group()

                except (ValueError, TypeError):
                    # Продолжаем поиск с другими паттернами при ошибках парсинга
                    continue

        return None

    def validate_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        """
        Валидирует диапазон дат
        """
        if start_date > end_date:
            return False

        # Проверяем, что диапазон не слишком большой (больше года)
        if (end_date - start_date).days > 365:
            return False

        return True

    def _get_target_year_for_month(self, month: int) -> int:
        """
        Определяет целевой год для месяца.
        Если месяц уже прошёл в этом году, возвращает следующий год.
        """
        now = datetime.now(TZ)
        year = now.year
        if month < now.month:
            year += 1
        return year

    def extract_dates_from_text(self, text: str) -> Tuple[datetime, datetime, str]:
        """
        Основной метод для извлечения дат из текста.
        Пробует разные стратегии: диапазон -> конкретная дата -> месяц
        """
        # Сначала пытаемся найти диапазон дат
        date_range = self.extract_date_range(text)
        if date_range:
            start_date, end_date, matched_text = date_range
            if self.validate_date_range(start_date, end_date):
                return start_date, end_date, matched_text

        # Если диапазон не найден, ищем конкретную дату
        specific_date = self.extract_specific_date(text)
        if specific_date:
            target_date, matched_text = specific_date
            # Для конкретной даты возвращаем диапазон из одного дня
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = target_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            return start_date, end_date, matched_text

        # Если конкретная дата не найдена, используем месячные границы
        return self.month_bounds_from_text(text)
