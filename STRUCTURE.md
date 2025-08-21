# Структура проекта

Проект построен на принципах Clean Architecture с использованием LangGraph для обработки диалогов.

## Архитектура

```
├─ apps/                    # Presentation Layer
│  └─ telegram_bot/         # Telegram Bot Application
│     ├─ main.py           # Точка входа бота
│     ├─ adapters/         # Адаптеры для внешних сервисов
│     ├─ handlers/         # Обработчики сообщений и callback
│     │  ├─ messages.py    # Обработчики текстовых сообщений
│     │  └─ callbacks.py   # Обработчики callback кнопок
│     ├─ middlewares/      # Middleware
│     │  └─ rate_limit.py  # Ограничение скорости запросов
│     ├─ keyboards/        # Клавиатуры
│     └─ dto/              # Data Transfer Objects
├─ core/                    # Core Layer
│  ├─ config.py            # Конфигурация приложения
│  ├─ di.py                # Dependency Injection
│  ├─ logging.py           # Настройка логирования
│  ├─ errors.py            # Обработка ошибок
│  └─ time.py              # Утилиты для работы со временем
├─ domain/                  # Domain Layer
│  └─ booking/              # Booking Domain
│     ├─ entities.py        # Доменные сущности
│     ├─ value_objects.py   # Value Objects
│     ├─ ports.py           # Порти (интерфейсы)
│     └─ policies.py        # Бизнес-правила
├─ application/             # Application Layer
│  ├─ services/             # Сервисы приложения
│  │  └─ booking_service.py # Сервис бронирования
│  └─ workflows/            # Workflows
│     └─ booking_orchestration.py # Оркестрация бронирования
├─ infrastructure/          # Infrastructure Layer
│  ├─ db/                   # База данных
│  │  ├─ models.py          # SQLAlchemy модели
│  │  ├─ repositories.py    # Реализации репозиториев
│  │  └─ migrations/        # Alembic миграции
│  ├─ kv/                   # Key-Value хранилище
│  │  └─ redis_client.py    # Redis клиент
│  ├─ vector/               # Векторная база данных
│  │  └─ chroma_client.py   # ChromaDB клиент
│  ├─ security/             # Безопасность
│  │  └─ input_guard.py     # Валидация входных данных
│  ├─ telemetry/            # Телеметрия
│  │  └─ traces.py          # OpenTelemetry трейсы
│  └─ llm/                  # LLM инфраструктура
│     ├─ prompts/           # Промпты
│     │  ├─ extract_booking.ru.md
│     │  └─ guardrails.md
│     ├─ tools/             # Инструменты
│     │  ├─ check_availability_tool.py
│     │  ├─ search_knowledge_tool.py
│     │  ├─ datetime_helper.py  # Функции работы с датой/временем
│     │  └─ string_helper.py    # Функции работы со строками
│     └─ graphs/            # LangGraph графы
│        ├─ state.py        # Состояния графов
│        ├─ checkpointer.py # Настройки checkpointer
│        ├─ booking/        # Граф бронирования
│        │  ├─ nodes.py     # Узлы графа бронирования
│        │  └─ graph.py     # build_booking_graph()
│        └─ router/         # Граф роутера
│           ├─ nodes.py     # Узлы роутера
│           └─ graph.py     # build_main_graph()
├─ tests/                   # Тесты
│  ├─ unit/                 # Unit тесты
│  │  ├─ test_policies.py
│  │  └─ test_slot_calc.py
│  ├─ integration/          # Integration тесты
│  │  └─ test_booking_flow.py
│  └─ e2e/                  # End-to-end тесты
│     └─ test_bot_dialog.py
├─ scripts/                 # Скрипты
│  └─ dev_bootstrap.py      # Скрипт для разработки
├─ docker/                  # Docker
│  ├─ Dockerfile
│  └─ docker-compose.yml
├─ old/                     # Старая реализация
│  ├─ agent/                # Старые агенты
│  ├─ halper/               # Старые helper функции
│  ├─ handlers/             # Старые обработчики
│  ├─ models/               # Старые модели
│  ├─ services/             # Старые сервисы
│  ├─ data/                 # Старые данные
│  └─ main.py               # Старая точка входа
├─ .env.example             # Пример переменных окружения
├─ pyproject.toml           # Конфигурация проекта
├─ README.md                # Документация
├─ Makefile                 # Команды для разработки
└─ STRUCTURE.md             # Этот файл
```

## Принципы архитектуры

### Clean Architecture
- **Independence of Frameworks**: Архитектура не зависит от внешних фреймворков
- **Testability**: Бизнес-логика может быть протестирована без UI, БД, веб-серверов
- **Independence of UI**: UI может легко изменяться без изменения остальной системы
- **Independence of Database**: Бизнес-правила не связаны с БД
- **Independence of any external agency**: Бизнес-правила не знают ничего о внешнем мире

### Dependency Rule
Зависимости направлены внутрь, к доменной логике:
- Внешние слои зависят от внутренних
- Внутренние слои не зависят от внешних
- Доменная логика не зависит ни от чего

### Слои

1. **Domain Layer** - Бизнес-логика и правила
2. **Application Layer** - Use cases и координация
3. **Infrastructure Layer** - Внешние сервисы и БД
4. **Presentation Layer** - UI и API

## Миграция со старой архитектуры

Старая реализация перенесена в папку `old/` и включает:
- Простые функции-helper
- Базовые графы LangGraph
- Простые обработчики Telegram

Новая архитектура:
- Разделяет ответственности по слоям
- Использует dependency injection
- Поддерживает тестирование
- Масштабируема и поддерживаема
