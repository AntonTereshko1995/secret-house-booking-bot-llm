# Secret House Booking Bot

Telegram бот для бронирования секретного дома с использованием LLM и LangGraph.

## Архитектура

Проект построен на принципах Clean Architecture:

```
├─ apps/                    # Presentation Layer
│  └─ telegram_bot/         # Telegram Bot Application
├─ core/                    # Core Layer
├─ domain/                  # Domain Layer
│  └─ booking/              # Booking Domain
├─ application/             # Application Layer
└─ infrastructure/          # Infrastructure Layer
```

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/secret-house-booking-bot.git
cd secret-house-booking-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -e .
pip install -e ".[dev]"
```

4. Скопируйте `.env.example` в `.env` и настройте переменные окружения:
```bash
cp .env.example .env
```

5. Запустите бота:
```bash
python apps/telegram_bot/main.py
```

## Разработка

### Запуск тестов
```bash
pytest
```

### Линтинг и форматирование
```bash
black .
isort .
ruff check .
mypy .
```

### Pre-commit hooks
```bash
pre-commit install
```

## Структура проекта

- `apps/` - Приложения (Telegram Bot)
- `core/` - Ядро приложения (конфигурация, DI, логирование)
- `domain/` - Доменная логика (сущности, value objects, порты)
- `application/` - Слой приложения (сервисы, workflows)
- `infrastructure/` - Инфраструктура (БД, Redis, LLM, графы)
- `tests/` - Тесты (unit, integration, e2e)

## Лицензия

MIT License
