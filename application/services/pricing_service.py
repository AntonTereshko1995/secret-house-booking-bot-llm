"""
Сервис ценообразования
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from core.config import settings
from core.logging import get_logger
from domain.booking.pricing import (
    AddOnService,
    PricingBreakdown,
    PricingRequest,
    PricingResponse,
    TariffRate,
)

TZ = ZoneInfo(settings.timezone)
logger = get_logger(__name__)


class PricingService:
    """Сервис для расчета стоимости аренды с загрузкой конфигурации из JSON файла"""

    def __init__(self):
        self.tariff_rates = self._load_tariff_rates()
        self.add_on_services = self._load_add_on_services()

    def _load_tariff_rates(self) -> dict[int, TariffRate]:
        """Загружает тарифы из JSON файла конфигурации"""
        try:
            config_path = Path(settings.pricing_config_path)
            if not config_path.exists():
                logger.error(f"Pricing config file not found: {config_path}")
                return {}

            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)

            tariffs = {}
            for tariff_data in data.get("rental_prices", []):
                # Конвертируем цены в Decimal для точных расчетов
                tariff_data = self._convert_prices_to_decimal(tariff_data)
                tariff = TariffRate(**tariff_data)
                tariffs[tariff.tariff] = tariff

            logger.info(f"Loaded {len(tariffs)} tariff rates from config")
            return tariffs

        except Exception:
            logger.exception("Error loading tariff rates from config")
            return {}

    def _convert_prices_to_decimal(self, tariff_data: dict) -> dict:
        """Конвертирует денежные значения в Decimal"""
        price_fields = [
            "price",
            "sauna_price",
            "secret_room_price",
            "second_bedroom_price",
            "extra_hour_price",
            "extra_people_price",
            "photoshoot_price",
        ]

        for field in price_fields:
            if field in tariff_data:
                tariff_data[field] = Decimal(str(tariff_data[field]))

        # Конвертируем multi_day_prices
        if "multi_day_prices" in tariff_data:
            multi_day_prices = {}
            for days, price in tariff_data["multi_day_prices"].items():
                multi_day_prices[days] = Decimal(str(price))
            tariff_data["multi_day_prices"] = multi_day_prices

        return tariff_data

    def _load_add_on_services(self) -> dict[str, AddOnService]:
        """Загружает дополнительные услуги"""
        services = {
            "sauna": AddOnService(
                service_id="sauna",
                name="Сауна",
                price=Decimal("100"),
                is_per_hour=False,
                description="Сауна для отдыха",
            ),
            "photoshoot": AddOnService(
                service_id="photoshoot",
                name="Фотосъемка",
                price=Decimal("100"),
                is_per_hour=False,
                description="Профессиональная фотосъемка",
            ),
            "secret_room": AddOnService(
                service_id="secret_room",
                name="Секретная комната",
                price=Decimal("70"),
                is_per_hour=False,
                description="Доступ к секретной комнате",
            ),
            "second_bedroom": AddOnService(
                service_id="second_bedroom",
                name="Вторая спальня",
                price=Decimal("70"),
                is_per_hour=False,
                description="Доступ ко второй спальне",
            ),
        }
        return services

    async def calculate_pricing(self, request: PricingRequest) -> PricingResponse:
        """Расчет стоимости аренды"""
        try:
            # Определяем тариф
            tariff = await self._get_tariff_for_request(request)
            if not tariff:
                raise ValueError(
                    f"Неизвестный тариф: {request.tariff or request.tariff_id}"
                )

            # Определяем количество дней
            duration_days = self._calculate_duration_days(request, tariff)

            # Базовая стоимость
            base_cost = self._calculate_base_cost(tariff, duration_days)

            # Дополнительные услуги
            add_on_costs = await self._calculate_add_on_costs(request, tariff)
            total_add_on_cost = sum(add_on_costs.values())

            # Общая стоимость
            total_cost = base_cost + total_add_on_cost

            # Создаем детализацию
            breakdown = PricingBreakdown(
                tariff_name=tariff.name,
                tariff_id=tariff.tariff,
                base_cost=base_cost,
                duration_hours=tariff.duration_hours,
                duration_days=duration_days,
                add_on_costs=add_on_costs,
                total_cost=total_cost,
                max_people=tariff.max_people,
                includes_transfer=tariff.is_transfer,
                includes_photoshoot=tariff.is_photoshoot
                and tariff.photoshoot_price == 0,
            )

            # Форматируем сообщение
            formatted_message = self._format_pricing_message(breakdown, tariff)
            booking_suggestion = self._generate_booking_suggestion(breakdown)

            return PricingResponse(
                breakdown=breakdown,
                formatted_message=formatted_message,
                booking_suggestion=booking_suggestion,
                valid_until=datetime.now(TZ) + timedelta(hours=24),
            )

        except Exception:
            logger.exception(
                "Error calculating pricing", extra={"request": request.dict()}
            )
            raise

    async def _get_tariff_for_request(
        self, request: PricingRequest
    ) -> TariffRate | None:
        """Определяет подходящий тариф для запроса"""
        if request.tariff_id is not None:
            return self.tariff_rates.get(request.tariff_id)

        if request.tariff:
            # Поиск по названию или ключевым словам
            tariff_lower = request.tariff.lower()

            # Точные совпадения
            for tariff in self.tariff_rates.values():
                tariff_name_lower = tariff.name.lower()

                # Суточные тарифы
                if "суточн" in tariff_lower:
                    if "суточн" in tariff_name_lower:
                        if "двоих" in tariff_lower and "двоих" in tariff_name_lower:
                            return tariff
                        elif "3 человек" in tariff_name_lower or (
                            "двоих" not in tariff_lower
                            and "двоих" not in tariff_name_lower
                        ):
                            return tariff

                # 12-часовые тарифы
                if "12" in tariff_lower and "12" in tariff.name:
                    if "инкогнито" in tariff_lower and "инкогнито" in tariff_name_lower:
                        return tariff
                    elif "инкогнито" not in tariff_lower:
                        return tariff

                # Рабочий тариф
                if "рабочий" in tariff_lower and "рабочий" in tariff_name_lower:
                    return tariff

                # Инкогнито
                if "инкогнито" in tariff_lower and "инкогнито" in tariff_name_lower:
                    if "день" in tariff_lower and "день" in tariff_name_lower:
                        return tariff
                    elif "12" in tariff_lower and "12" in tariff.name:
                        return tariff

                # Абонементы
                if "абонемент" in tariff_lower and "абонемент" in tariff_name_lower:
                    if "3" in tariff_lower and tariff.subscription_type == 3:
                        return tariff
                    elif "5" in tariff_lower and tariff.subscription_type == 5:
                        return tariff
                    elif "8" in tariff_lower and tariff.subscription_type == 8:
                        return tariff

        # По умолчанию - суточный тариф от 3 человек
        return self.tariff_rates.get(1)

    def _calculate_duration_days(
        self, request: PricingRequest, tariff: TariffRate
    ) -> int:
        """Вычисляет количество дней"""
        if request.duration_days:
            return request.duration_days

        if request.start_date and request.end_date:
            delta = request.end_date - request.start_date
            return max(1, delta.days)

        return 1

    def _calculate_base_cost(self, tariff: TariffRate, duration_days: int) -> Decimal:
        """Рассчитывает базовую стоимость"""
        if duration_days == 1:
            return tariff.price

        # Многодневное бронирование
        if tariff.multi_day_prices:
            day_key = str(duration_days)
            if day_key in tariff.multi_day_prices:
                return tariff.multi_day_prices[day_key]

            # Если точного количества дней нет, берем максимальное доступное
            max_days = max(
                [int(k) for k in tariff.multi_day_prices.keys() if k.isdigit()]
            )
            if duration_days > max_days:
                # Рассчитываем пропорционально
                base_for_max_days = tariff.multi_day_prices[str(max_days)]
                return (
                    base_for_max_days
                    * Decimal(str(duration_days))
                    / Decimal(str(max_days))
                )

        # Если многодневных цен нет, используем базовую цену за день
        return tariff.price * duration_days

    async def _calculate_add_on_costs(
        self, request: PricingRequest, tariff: TariffRate
    ) -> dict[str, Decimal]:
        """Рассчитывает стоимость дополнительных услуг"""
        costs = {}

        for service_id in request.add_ons:
            if service_id == "sauna" and tariff.sauna_price > 0:
                costs["Сауна"] = tariff.sauna_price
            elif service_id == "secret_room" and tariff.secret_room_price > 0:
                costs["Секретная комната"] = tariff.secret_room_price
            elif service_id == "second_bedroom" and tariff.second_bedroom_price > 0:
                costs["Вторая спальня"] = tariff.second_bedroom_price
            elif service_id == "photoshoot" and tariff.photoshoot_price > 0:
                costs["Фотосъемка"] = tariff.photoshoot_price

        return costs

    def _format_pricing_message(
        self, breakdown: PricingBreakdown, tariff: TariffRate
    ) -> str:
        """Форматирует сообщение о стоимости на русском языке"""
        message = f"💰 **{breakdown.tariff_name}**\n\n"

        message += "📊 **Стоимость аренды:**\n"
        message += f"• Базовая стоимость: {breakdown.base_cost} руб."

        if breakdown.duration_days > 1:
            message += f" ({breakdown.duration_days} дн.)"
        else:
            message += f" ({breakdown.duration_hours} ч.)"

        message += f"\n• Максимум гостей: {breakdown.max_people} чел.\n"

        # Что включено в тариф
        includes = []
        if breakdown.includes_transfer:
            includes.append("трансфер")
        if breakdown.includes_photoshoot:
            includes.append("фотосъемка")

        if includes:
            message += f"• Включено: {', '.join(includes)}\n"

        # Дополнительные услуги
        if breakdown.add_on_costs:
            message += "\n📋 **Дополнительные услуги:**\n"
            for service_name, cost in breakdown.add_on_costs.items():
                message += f"• {service_name}: {cost} руб.\n"

        # Итоговая стоимость
        message += f"\n💳 **Итого: {breakdown.total_cost} руб.**"

        # Информация об ограничениях
        if tariff.is_check_in_time_limit:
            message += "\n\n⏰ *Тариф с ограничением по времени заезда*"

        # Информация об абонементе
        if tariff.subscription_type > 0:
            message += f"\n\n🎫 *Абонемент на {tariff.subscription_type} посещений*"

        return message

    def _generate_booking_suggestion(self, breakdown: PricingBreakdown) -> str:
        """Генерирует предложение для бронирования"""
        suggestions = [
            "🎯 Хотите забронировать? Укажите желаемые даты и время.",
            "📅 Готовы к бронированию? Напишите конкретные даты вашего визита.",
            "✨ Для бронирования укажите даты заезда и выезда.",
        ]

        if breakdown.duration_days > 1:
            suggestions.append(
                "🏡 Для многодневного бронирования уточните точные даты."
            )

        return suggestions[0]

    async def get_available_tariffs(self) -> list[TariffRate]:
        """Возвращает список доступных тарифов"""
        return list(self.tariff_rates.values())

    async def get_tariff_by_id(self, tariff_id: int) -> TariffRate | None:
        """Возвращает тариф по ID"""
        return self.tariff_rates.get(tariff_id)

    async def get_tariffs_summary(self) -> str:
        """Возвращает краткую сводку всех тарифов"""
        tariffs = await self.get_available_tariffs()

        message = "📋 **Доступные тарифы:**\n\n"

        for tariff in sorted(tariffs, key=lambda x: x.tariff):
            message += f"**{tariff.name}**\n"
            message += f"• Цена: от {tariff.price} руб.\n"
            message += f"• Длительность: {tariff.duration_hours} ч.\n"
            message += f"• Максимум гостей: {tariff.max_people} чел.\n"

            if tariff.is_transfer:
                message += "• Включен трансфер\n"
            if tariff.is_photoshoot and tariff.photoshoot_price == 0:
                message += "• Включена фотосъемка\n"

            message += "\n"

        return message
