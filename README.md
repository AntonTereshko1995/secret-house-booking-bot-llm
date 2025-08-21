# Secret House Booking Bot

Telegram bot for booking a secret house using LLM and LangGraph.

## Architecture

The project is built on Clean Architecture principles:

```
├─ apps/                    # Presentation Layer
│  └─ telegram_bot/         # Telegram Bot Application
├─ core/                    # Core Layer
├─ domain/                  # Domain Layer
│  └─ booking/              # Booking Domain
├─ application/             # Application Layer
└─ infrastructure/          # Infrastructure Layer
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/secret-house-booking-bot.git
cd secret-house-booking-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -e .
pip install -e ".[dev]"
```

4. Copy `.env.example` to `.env` and configure environment variables:
```bash
cp .env.example .env
```

5. Run the bot:
```bash
python apps/telegram_bot/main.py
```

## Development

### Running tests
```bash
pytest
```

### Linting and formatting
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

## Project Structure

- `apps/` - Applications (Telegram Bot)
- `core/` - Application core (configuration, DI, logging)
- `domain/` - Domain logic (entities, value objects, ports)
- `application/` - Application layer (services, workflows)
- `infrastructure/` - Infrastructure (DB, Redis, LLM, graphs)
- `tests/` - Tests (unit, integration, e2e)

## License

MIT License
