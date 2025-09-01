"""
Экстрактор для извлечения требований к ценообразованию из естественного языка
"""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from core.config import settings
from core.logging import get_logger
from domain.booking.pricing import PricingRequest
from infrastructure.llm.extractors.date_extractor import DateExtractor

TZ = ZoneInfo(settings.timezone)
logger = get_logger(__name__)


class PricingExtractor:
    """Экстрактор для извлечения параметров ценообразования из текста"""

    def __init__(self):
        self.date_extractor = DateExtractor()

        # Паттерны для тарифов
        self.tariff_patterns = {
            # Русские паттерны
            "суточно от 3": ["суточн.*3.*человек", "суточн.*троих", "суточн.*три.*чел"],
            "суточно для двоих": ["суточн.*двоих", "суточн.*2.*человек", "суточн.*двух.*чел"],
            "12 часов": ["12.*час", "двенадцать.*час", "полсуток"],
            "рабочий": ["рабочий", "дневной", "будний"],
            "инкогнито день": ["инкогнито.*день", "инкогнито.*24", "инкогнито.*сутки"],
            "инкогнито 12": ["инкогнито.*12", "инкогнито.*полсуток"],
            "абонемент 3": ["абонемент.*3", "три.*посещения", "3.*посещения"],
            "абонемент 5": ["абонемент.*5", "пять.*посещений", "5.*посещений"],
            "абонемент 8": ["абонемент.*8", "восемь.*посещений", "8.*посещений"],

            # Английские паттерны
            "daily for 3": ["daily.*3.*people", "daily.*three.*people"],
            "daily for 2": ["daily.*2.*people", "daily.*two.*people", "daily.*couple"],
            "12 hours": ["12.*hours", "twelve.*hours", "half.*day"],
            "working": ["working.*hours", "business.*hours"],
            "incognito day": ["incognito.*day", "incognito.*24"],
            "incognito 12": ["incognito.*12", "incognito.*half"],
            "subscription": ["subscription", "package", "membership"],
        }

        # Паттерны для дополнительных услуг
        self.addon_patterns = {
            "sauna": ["сауна", "баня", "sauna", "steam"],
            "photoshoot": ["фото", "съемка", "фотосессия", "photo", "shoot", "photography"],
            "secret_room": ["секретн.*комната", "тайн.*комната", "secret.*room", "hidden.*room"],
            "second_bedroom": ["втор.*спальня", "дополн.*спальня", "second.*bedroom", "extra.*bedroom"],
        }

    async def extract_pricing_requirements(self, text: str) -> PricingRequest:
        """Извлекает требования к ценообразованию из текста"""
        try:
            text_lower = text.lower().strip()

            # Извлекаем тариф
            tariff = self._extract_tariff(text_lower)

            # Извлекаем дополнительные услуги
            add_ons = self._extract_addons(text_lower)

            # Извлекаем количество гостей
            number_guests = self._extract_guest_count(text_lower)

            # Извлекаем временные параметры
            duration_days, start_date, end_date = self._extract_time_parameters(text)

            # Создаем запрос
            request = PricingRequest(
                tariff=tariff,
                add_ons=add_ons,
                number_guests=number_guests,
                duration_days=duration_days,
                start_date=start_date,
                end_date=end_date,
            )

            logger.debug(
                "Extracted pricing requirements",
                extra={
                    "original_text": text,
                    "extracted_request": request.dict(exclude_none=True)
                }
            )

            return request

        except Exception:
            logger.exception("Error extracting pricing requirements", extra={"text": text})
            # Возвращаем базовый запрос при ошибке
            return PricingRequest()

    def _extract_tariff(self, text: str) -> str | None:
        """Извлекает тип тарифа из текста"""

        # Проверяем каждый паттерн тарифа
        for tariff_key, patterns in self.tariff_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Маппинг на внутренние названия тарифов
                    tariff_mapping = {
                        "суточно от 3": "суточно от 3 человек",
                        "daily for 3": "суточно от 3 человек",
                        "суточно для двоих": "суточно для двоих",
                        "daily for 2": "суточно для двоих",
                        "12 часов": "12 часов",
                        "12 hours": "12 часов",
                        "рабочий": "рабочий",
                        "working": "рабочий",
                        "инкогнито день": "инкогнито день",
                        "incognito day": "инкогнито день",
                        "инкогнито 12": "инкогнито 12",
                        "incognito 12": "инкогнито 12",
                        "абонемент 3": "абонемент 3",
                        "абонемент 5": "абонемент 5",
                        "абонемент 8": "абонемент 8",
                        "subscription": "абонемент 3",  # По умолчанию 3 посещения
                    }
                    return tariff_mapping.get(tariff_key)

        # Если ничего не найдено, анализируем общие ключевые слова
        if any(word in text for word in ["сутки", "день", "daily", "24"]):
            # Проверяем на количество людей
            if any(word in text for word in ["двоих", "2", "два", "couple", "two"]):
                return "суточно для двоих"
            else:
                return "суточно от 3 человек"
        elif any(word in text for word in ["12", "полсуток", "half"]):
            return "12 часов"
        elif any(word in text for word in ["абонемент", "subscription", "package"]):
            return "абонемент 3"

        return None

    def _extract_addons(self, text: str) -> list[str]:
        """Извлекает дополнительные услуги из текста"""
        addons = []

        for addon_id, patterns in self.addon_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if addon_id not in addons:
                        addons.append(addon_id)
                    break

        return addons

    def _extract_guest_count(self, text: str) -> int | None:
        """Извлекает количество гостей из текста"""

        # Паттерны для чисел
        number_patterns = [
            (r"(\d+)\s*(?:человек|чел|людей|гост|people|guests|persons)", lambda m: int(m.group(1))),
            (r"(?:один|одного|1)\s*(?:человек|чел|гост)", lambda m: 1),
            (r"(?:два|двух|двоих|2)\s*(?:человек|чел|гост|людей)", lambda m: 2),
            (r"(?:три|трех|троих|3)\s*(?:человек|чел|гост|людей)", lambda m: 3),
            (r"(?:четыре|четырех|4)\s*(?:человек|чел|гост|людей)", lambda m: 4),
            (r"(?:пять|пятеро|5)\s*(?:человек|чел|гост|людей)", lambda m: 5),
            (r"(?:шесть|шестеро|6)\s*(?:человек|чел|гост|людей)", lambda m: 6),
        ]

        for pattern, extract_func in number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return extract_func(match)
                except (ValueError, AttributeError):
                    continue

        # Специальные случаи
        if any(word in text for word in ["один", "одного", "solo", "single", "alone"]):
            return 1
        elif any(word in text for word in ["пара", "двоих", "couple", "pair"]):
            return 2
        elif any(word in text for word in ["компания", "группа", "company", "group"]):
            return 4  # Предполагаем среднюю компанию

        return None

    def _extract_time_parameters(self, text: str) -> tuple[int | None, datetime | None, datetime | None]:
        """Извлекает временные параметры (дни, даты)"""
        duration_days = None
        start_date = None
        end_date = None

        try:
            # Извлекаем даты с помощью существующего экстрактора
            dates_result = self.date_extractor.extract_dates_from_text(text)
            if dates_result:
                start_date, end_date, _ = dates_result

                # Рассчитываем количество дней
                if start_date and end_date:
                    delta = end_date - start_date
                    duration_days = max(1, delta.days)
        except Exception as e:
            logger.debug("Error extracting dates for pricing", extra={"error": str(e)})

        # Извлекаем количество дней из текста
        text_lower = text.lower()

        day_patterns = [
            (r"(\d+)\s*(?:дней|дня|день|days?)", lambda m: int(m.group(1))),
            (r"(?:один|одного|1)\s*(?:день|дня)", lambda m: 1),
            (r"(?:два|двух|2)\s*(?:дня|день)", lambda m: 2),
            (r"(?:три|трех|3)\s*(?:дня|день)", lambda m: 3),
            (r"(?:неделя|week)", lambda m: 7),
            (r"(?:две|2)\s*(?:недели|weeks)", lambda m: 14),
        ]

        for pattern, extract_func in day_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    extracted_days = extract_func(match)
                    if not duration_days:  # Используем только если не извлекли из дат
                        duration_days = extracted_days
                    break
                except (ValueError, AttributeError):
                    continue

        return duration_days, start_date, end_date

    def is_pricing_query(self, text: str) -> bool:
        """Проверяет, является ли текст запросом о ценах"""
        text_lower = text.lower()

        pricing_keywords = [
            # Русские
            "цена", "цены", "стоимость", "сколько стоит", "прайс", "расценки",
            "тариф", "тарифы", "прайс-лист", "стоит ли", "цену", "цене",
            "дешево", "дорого", "бюджет", "расходы", "затрат",

            # Английские
            "price", "cost", "how much", "pricing", "rate", "rates",
            "tariff", "fee", "charge", "expensive", "cheap", "budget"
        ]

        return any(keyword in text_lower for keyword in pricing_keywords)

    def extract_comparison_request(self, text: str) -> bool:
        """Проверяет, просит ли пользователь сравнение тарифов"""
        text_lower = text.lower()

        comparison_keywords = [
            "сравни", "сравнить", "разница", "различие", "отличие",
            "что лучше", "какой выбрать", "посоветуй", "recommend",
            "compare", "difference", "better", "best", "choose"
        ]

        return any(keyword in text_lower for keyword in comparison_keywords)
