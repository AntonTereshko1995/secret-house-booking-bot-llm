"""
House Information Context System for LLM-powered FAQ
Содержит полную информацию о The Secret House для использования в LLM промптах
"""

from domain.faq.entities import HouseInformation


class HouseContextBuilder:
    """Builder for house information context used in LLM prompts"""

    def __init__(self):
        self.house_info = self._build_house_information()

    def _load_pricing_config(self) -> dict:
        """Load pricing configuration from JSON file"""
        import json
        from core.config import settings
        
        with open(settings.pricing_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_tariffs_from_config(self, pricing_config: dict) -> list:
        """Build tariffs list from pricing configuration"""
        tariffs = []
        
        for rental_price in pricing_config.get("rental_prices", []):
            tariff_name = rental_price.get("name", "")
            
            # Map tariff IDs to display names
            if rental_price.get("tariff") == 1:
                tariff_name = "ТАРИФ 'СУТОЧНО ОТ 3 ЧЕЛОВЕК'"
                tariff = {
                    "name": tariff_name,
                    "prices": {},
                    "extras": {},
                    "features": [
                        "Доступ ко всем комнатам дома",
                        f"Максимальное количество гостей — {rental_price.get('max_people', 6)}",
                        "Свободный выбор времени заезда",
                    ],
                    "bonus": "При бронировании от 2 дней — дарим 12 часов в подарок при повторном бронировании!"
                }
                
                # Build multi-day prices
                multi_day_prices = rental_price.get("multi_day_prices", {})
                for days, price in multi_day_prices.items():
                    if int(days) <= 3:
                        day_text = f"{days} день" if days == "1" else f"{days} дня"
                        tariff["prices"][day_text] = f"{price} BYN"
                
                # Add extras
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("photoshoot_price", 0) > 0:
                    tariff["extras"]["Фотосессия"] = f"{rental_price['photoshoot_price']} BYN"
                
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 7:
                tariff_name = "ТАРИФ 'СУТОЧНО ДЛЯ ПАР'"
                tariff = {
                    "name": tariff_name,
                    "prices": {},
                    "extras": {},
                    "features": [
                        "Доступ ко всем комнатам дома",
                        f"Максимальное количество гостей — {rental_price.get('max_people', 2)}",
                        "Свободный выбор времени заезда",
                    ],
                    "bonus": "При бронировании от 2 дней — дарим 12 часов в подарок при повторном бронировании!"
                }
                
                # Build multi-day prices
                multi_day_prices = rental_price.get("multi_day_prices", {})
                for days, price in multi_day_prices.items():
                    if int(days) <= 3:
                        day_text = f"{days} день" if days == "1" else f"{days} дня"
                        tariff["prices"][day_text] = f"{price} BYN"
                
                # Add extras
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("photoshoot_price", 0) > 0:
                    tariff["extras"]["Фотосессия"] = f"{rental_price['photoshoot_price']} BYN"
                
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 0:
                tariff = {
                    "name": "ТАРИФ '12 ЧАСОВ'",
                    "price": f"{rental_price.get('price', 250)} BYN",
                    "extras": {},
                    "features": [
                        "Включает одну спальню на выбор",
                        f"Максимальное количество гостей — {rental_price.get('max_people', 2)}",
                        "Свободный выбор времени заезда",
                    ]
                }
                
                # Add extras
                if rental_price.get("secret_room_price", 0) > 0:
                    tariff["extras"]["Секретная комната"] = f"{rental_price['secret_room_price']} BYN"
                if rental_price.get("second_bedroom_price", 0) > 0:
                    tariff["extras"]["Доступ ко второй спальне"] = f"{rental_price['second_bedroom_price']} BYN"
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("extra_hour_price", 0) > 0:
                    tariff["extras"]["Дополнительный 1 час"] = f"{rental_price['extra_hour_price']} BYN"
                
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 2:
                tariff = {
                    "name": "ТАРИФ 'РАБОЧИЙ' (с понедельника по четверг)",
                    "price": f"{rental_price.get('price', 180)} BYN",
                    "extras": {},
                    "features": [
                        "Включает одну спальню на выбор",
                        f"Максимальное количество гостей — {rental_price.get('max_people', 2)}",
                        "Бронирование: с 11:00 до 20:00 или с 22:00 до 09:00",
                    ]
                }
                
                # Add extras
                if rental_price.get("secret_room_price", 0) > 0:
                    tariff["extras"]["Секретная комната"] = f"{rental_price['secret_room_price']} BYN"
                if rental_price.get("second_bedroom_price", 0) > 0:
                    tariff["extras"]["Доступ ко второй спальне"] = f"{rental_price['second_bedroom_price']} BYN"
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("extra_hour_price", 0) > 0:
                    tariff["extras"]["Дополнительный 1 час"] = f"{rental_price['extra_hour_price']} BYN"
                
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 3:
                tariff = {
                    "name": "ТАРИФ 'ИНКОГНИТО' (VIP-опция)",
                    "prices": {"Сутки": f"{rental_price.get('price', 900)} BYN"},
                    "features": [
                        "Доступ ко всем комнатам дома",
                        "Без заключения договора",
                        "Отключение внешних камер наблюдения по периметру дома",
                    ],
                    "gifts": [
                        "Трансфер от/до дома на автомобиле бизнес-класса",
                        "Бутылка вина, лёгкие закуски и сауна",
                        "Бесплатная фотосессия при аренде на сутки (2 часа, бронь за неделю)",
                    ]
                }
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 4:
                tariff = {
                    "name": "ТАРИФ 'ИНКОГНИТО' (VIP-опция)",
                    "prices": {"12 часов": f"{rental_price.get('price', 600)} BYN"},
                    "features": [
                        "Доступ ко всем комнатам дома",
                        "Без заключения договора",
                        "Отключение внешних камер наблюдения по периметру дома",
                    ],
                    "gifts": [
                        "Трансфер от/до дома на автомобиле бизнес-класса",
                        "Бутылка вина, лёгкие закуски и сауна",
                    ]
                }
                # Check if this tariff already exists (merge with tariff 3)
                existing_incognito = None
                for t in tariffs:
                    if "ИНКОГНИТО" in t["name"]:
                        existing_incognito = t
                        break
                
                if existing_incognito:
                    existing_incognito["prices"]["12 часов"] = f"{rental_price.get('price', 600)} BYN"
                else:
                    tariffs.append(tariff)
                    
            elif rental_price.get("tariff") == 5:
                tariff = {
                    "name": "Абонемент на 3 посещения",
                    "price": f"{rental_price.get('price', 680)} BYN",
                    "duration": "12 часов",
                    "extras": {},
                    "features": [f"Максимальное количество гостей — {rental_price.get('max_people', 3)}"]
                }
                
                # Add extras
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("extra_hour_price", 0) > 0:
                    tariff["extras"]["Дополнительный 1 час"] = f"{rental_price['extra_hour_price']} BYN"
                
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 6:
                tariff = {
                    "name": "Абонемент на 5 посещений",
                    "price": f"{rental_price.get('price', 1000)} BYN",
                    "duration": "12 часов",
                    "extras": {},
                    "features": [f"Максимальное количество гостей — {rental_price.get('max_people', 3)}"]
                }
                
                # Add extras
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("extra_hour_price", 0) > 0:
                    tariff["extras"]["Дополнительный 1 час"] = f"{rental_price['extra_hour_price']} BYN"
                
                tariffs.append(tariff)
                
            elif rental_price.get("tariff") == 8:
                tariff = {
                    "name": "Абонемент на 8 посещений",
                    "price": f"{rental_price.get('price', 1600)} BYN",
                    "duration": "12 часов",
                    "extras": {},
                    "features": [f"Максимальное количество гостей — {rental_price.get('max_people', 3)}"]
                }
                
                # Add extras
                if rental_price.get("sauna_price", 0) > 0:
                    tariff["extras"]["Сауна"] = f"{rental_price['sauna_price']} BYN"
                if rental_price.get("extra_hour_price", 0) > 0:
                    tariff["extras"]["Дополнительный 1 час"] = f"{rental_price['extra_hour_price']} BYN"
                
                tariffs.append(tariff)
        
        return tariffs

    def _build_house_information(self) -> HouseInformation:
        """Build comprehensive house information from user requirements"""
        # Load pricing configuration
        pricing_config = self._load_pricing_config()
        tariffs = self._build_tariffs_from_config(pricing_config)
        
        return HouseInformation(
            location="12 км от Минска направление агрогородок Ратомка, в окружении леса, уединённое место без посторонних, закрытая территория участка с автоматическими воротами",
            rooms={
                "green_bedroom": "стены зеленого цвета с добавлением дерева, регулируемая подсветка по периметру комнаты, кастомная кровать 2 на 2.20 метра из советских труб и кресло для фиксации рук и ног Turtur Chair для БДСМ игр, различные аксессуары для секса",
                "white_bedroom": "стены белого цвета с добавлением дерева, кастомная деревянная кровать в средневековом стиле с деревянной колодкой для рук и шеи, в комнате на стене есть зеркала, чтобы можно было подсматривать за всем процессом, различные аксессуары для секса",
                "kitchen": "холодильник, посудомойка, духовка, плита, вода из фильтра, кофе машина, посуда, различные бокалы, остров в центре кухни, на кухне есть перец, соль и оливковое масло",
                "living_room": "тантра кресло, камин, телевизор, качественная музыкальная аппаратура на 300 ват, выход на террасу, гостиная зона совмещенная с кухней",
                "sauna": "сухая сауна с электрическим отоплением, пано из можевельника, располагается 4 человека",
                "bathrooms": "на каждом этаже по ванной комнате. на первом душ, а на втором удобная ванная, гель для душа, шампунь, кондиционер, полотенце для рук, полотенце для ног, для каждого гостя есть халат и полотенце для тела",
                "secret_room": "Оснащена специальной мебелью и аксессуарами для взрослых, андреевский крест, ловушка tarantul, бондажный козел, oral table и различные аксессуары, подсветка по периметру комнаты, зеркальная стена и потолок",
                "bbq_area": "рядом с террасой есть bbq зона с мангалом, решеткой и шампурами. Так же есть дрова для камина и мангала",
            },
            amenities={
                "design": "две граффити в стиле Бэнкси, картины современных художников по всему дому, арт-объекты, геометрически расписаны стены в коридорах",
                "guest_kit": "каждому гостю предоставляется: халат, полотенце, гигиенический набор, одноразовая зубная щетка и паста, полотенце для тела, полотенце для рук, полотенце для ног, простынь в сауну",
                "cleaning": "уборка происходит после каждого клиента, на уборку тратится 2-3 часа, дизинфекция всех кожаных изделий, кварцевание помещений, влажная уборка дома, замена постельного белья и полотенцев",
                "check_in": "происходит без лишних лиц, самостоятельно. За 1 день до брони мы сообщим маршрут до дома и пароль от ключницы",
            },
            tariffs=tariffs,
            policies={
                "contract": "заключение договора обязательно (кроме тарифа Инкогнито)",
                "payment": "оплата наличкой или переводом на карту. мы берем 80 рублей в качестве предоплаты переводом по карте. После получения денег, мы вносим бронирование в календарь",
                "security": "Установлены камеры наблюдения по периметру дома. Для тарифа Инкогнито они отключаются",
                "certificates": "Гости могут приобрести сертификат по любому из тарифов для отдыха в доме",
            },
            contact_info={
                "admin_telegram": "@the_secret_house",
                "photos_link": "https://drive.google.com/drive/u/2/folders/14x2AMnkZJ8rgKa94U973CmMKWXa6feRw",
                "booking_instruction": "Напиши дату, время, тариф, количество гостей и мы создадим бронирование",
                "availability_check": "Если пользователь хочет узнать свободные даты в доме, то отправляй его в пункт меню 'Свободные датата' в телеграм боте",
                "certificates_purchase": "Для покупки сертификата нужно перейти в меню телеграм бота и выбрать пункт 'Приобрести подарочный сертификат'",
            },
        )

    def build_system_prompt(self) -> str:
        """Build comprehensive system prompt with house information"""
        return f"""Ты — виртуальный ассистент The Secret House, уникального загородного дома с современным искусством, стильными интерьерами и специальной «секретной комнатой» в стиле БДСМ. Твоя задача — отвечать на вопросы клиентов, помогая им узнать больше о доме, условиях аренды, тарифах и дополнительных услугах. Ты часть телеграм бота: там есть функционал по бронированию дома. На этот функционал нужно отправлять пользователя для брони.

ИНФОРМАЦИЯ О ДОМЕ:

ЛОКАЦИЯ:
{self.house_info.location}

КОМНАТЫ:
🛏 Зеленая спальня: {self.house_info.rooms["green_bedroom"]}

🛏 Белая спальня: {self.house_info.rooms["white_bedroom"]}

🍽 Кухня: {self.house_info.rooms["kitchen"]}

🛋 Гостиная: {self.house_info.rooms["living_room"]}

🧖‍♀️ Сауна: {self.house_info.rooms["sauna"]}

🛿 Ванные комнаты: {self.house_info.rooms["bathrooms"]}

🔥 Секретная комната: {self.house_info.rooms["secret_room"]}

🔥 BBQ зона: {self.house_info.rooms["bbq_area"]}

ДИЗАЙН И УДОБСТВА:
{self.house_info.amenities["design"]}

ГОСТЕВОЙ НАБОР:
{self.house_info.amenities["guest_kit"]}

ТАРИФЫ:
{self._format_tariffs()}

ПРАВИЛА И УСЛОВИЯ:
• Договор: {self.house_info.policies["contract"]}
• Оплата: {self.house_info.policies["payment"]}
• Безопасность: {self.house_info.policies["security"]}
• Сертификаты: {self.house_info.policies["certificates"]}

УБОРКА:
{self.house_info.amenities["cleaning"]}

ЗАСЕЛЕНИЕ:
{self.house_info.amenities["check_in"]}

ТВОЯ РОЛЬ:
- Будь дружелюбным, уверенным и немного игривым, но всегда уважительным
- Подчёркивай приватность, комфорт и уникальность атмосферы дома
- Отвечай ТОЛЬКО на русском языке
- При необходимости направляй пользователей к функциям бота

ФУНКЦИИ БОТА:
- Для бронирования: "{self.house_info.contact_info["booking_instruction"]}"
- Для свободных дат: "{self.house_info.contact_info["availability_check"]}"
- Для сертификатов: "{self.house_info.contact_info["certificates_purchase"]}"
- Для помощи администратора: "{self.house_info.contact_info["admin_telegram"]}"
- Фотографии дома: {self.house_info.contact_info["photos_link"]}

Если пользователь интересуется ценами, тарифами или услугами, давай конкретную информацию. Если просит советы по проведению времени в доме, предлагай варианты сценариев отдыха.

Если не знаешь ответ на вопрос, отправь пользователя к администратору {self.house_info.contact_info["admin_telegram"]}.
"""

    def _format_tariffs(self) -> str:
        """Format tariffs for system prompt"""
        tariff_text = ""
        for tariff in self.house_info.tariffs:
            tariff_text += f"\n📌 {tariff['name']}\n"

            if "prices" in tariff:
                for duration, price in tariff["prices"].items():
                    tariff_text += f"✔ {duration} — {price}\n"
            elif "price" in tariff:
                tariff_text += f"✔ {tariff['price']}\n"

            if "extras" in tariff:
                tariff_text += "Дополнительно:\n"
                for service, price in tariff["extras"].items():
                    tariff_text += f"{service} — {price}\n"

            if "features" in tariff:
                for feature in tariff["features"]:
                    tariff_text += f"- {feature}\n"

            if "bonus" in tariff:
                tariff_text += f"Бонус: {tariff['bonus']}\n"

            if "gifts" in tariff:
                tariff_text += "Подарки:\n"
                for gift in tariff["gifts"]:
                    tariff_text += f" {gift}\n"

            tariff_text += "\n"

        return tariff_text.strip()

    def get_house_information(self) -> HouseInformation:
        """Get structured house information"""
        return self.house_info
