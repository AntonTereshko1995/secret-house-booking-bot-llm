# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot for booking a "secret house" using LLM and LangGraph. The project implements Clean Architecture principles with a sophisticated LangGraph-based conversation flow for handling booking requests in natural language.

## Development Commands

### Essential Commands
- `make dev` - Run the bot in development mode  
- `make test` - Run all tests with pytest
- `make test-cov` - Run tests with coverage report
- `pytest tests/unit/` - Run only unit tests
- `pytest tests/integration/` - Run only integration tests
- `pytest tests/e2e/` - Run only end-to-end tests
- `pytest tests/path/to/test_file.py::test_function` - Run a single test
- `make lint` - Check code with all linters (black, isort, ruff, mypy)
- `make format` - Format code with black, isort, and ruff
- `make install` - Install dependencies for development

### Database Commands
- `make migrate` - Run Alembic migrations to latest
- `make migrate-create message="description"` - Create new migration

### Docker Commands
- `make docker-build` - Build Docker image
- `make docker-run` - Start services with docker-compose
- `make docker-stop` - Stop docker-compose services

## Architecture

The project follows Clean Architecture with these layers:

### Core Layer (`core/`)
- `config.py` - Pydantic settings with environment variables
- `logging.py` - Structured logging setup with structlog
- Contains utilities for datetime and string manipulation

### Domain Layer (`domain/`)
- `domain/booking/` - Core booking domain logic
- `entities.py` - Domain entities and business objects
- `ports.py` - Interfaces/ports for external dependencies

### Application Layer (`application/`)
- `services/booking_service.py` - Application services
- `workflows/` - Business workflows and orchestration

### Infrastructure Layer (`infrastructure/`)
- **LLM**: `infrastructure/llm/` - Contains the LangGraph implementation
  - `graphs/app/app_graph_builder.py` - Main application graph builder
  - `graphs/booking/` - Booking conversation flow
  - `graphs/common/graph_state.py` - Shared state definitions
  - `clients/openai_client.py` - OpenAI API integration
  - `extractors/` - Data extraction from natural language
- **Database**: `db/` - SQLAlchemy models and repositories
- **Key-Value**: `kv/` - Redis client for state storage
- **Vector DB**: `vector/` - ChromaDB for knowledge search

### Presentation Layer (`apps/`)
- `apps/telegram_bot/` - Telegram bot application
- `main.py` - Entry point for the bot
- `handlers/` - Message and callback handlers
- `middlewares/rate_limit.py` - Rate limiting middleware

## Key Technologies

- **LangGraph** - Conversation flow management with stateful graphs
- **Aiogram 3.x** - Modern async Telegram bot framework
- **SQLAlchemy 2.x** - Database ORM with async support
- **Redis** - State storage for FSM and graph checkpoints
- **ChromaDB** - Vector database for knowledge retrieval
- **Pydantic** - Data validation and settings management
- **OpenTelemetry** - Observability and tracing

## LangGraph Architecture

The bot uses a sophisticated multi-graph architecture:

1. **Main App Graph** (`app_graph_builder.py`):
   - Router node determines intent (booking, availability, FAQ, etc.)
   - Conditional routing to specialized subgraphs
   - Uses MemorySaver for conversation state persistence

2. **Booking Subgraph** (`booking/booking_graph.py`):
   - Handles multi-turn booking conversations
   - Extracts booking details from natural language
   - Validates availability and creates bookings

3. **State Management** (`common/graph_state.py`):
   - `AppState` - Main application state
   - Tracks conversation context, intent, and active subgraph

## Environment Variables

Required variables (see `.env.example`):
- `TELEGRAM_BOT_TOKEN` - Bot token from BotFather
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - LLM provider API key

Optional variables:
- `CHROMA_HOST`, `CHROMA_PORT` - Vector database configuration
- `OTEL_ENDPOINT` - OpenTelemetry collector endpoint
- `RATE_LIMIT_PER_MINUTE` - API rate limiting (default: 60)
- `TIMEZONE` - Application timezone (default: Europe/Minsk)

## Testing Strategy

- **Unit tests**: `tests/unit/` - Domain logic and utilities
- **Integration tests**: `tests/integration/` - Database and external services
- **E2E tests**: `tests/e2e/` - Full bot conversation flows

Test configuration in `pyproject.toml` includes coverage reporting and async support.

## Development Notes

- The project uses Russian language in comments and some UI text
- Main entry point: `python apps/telegram_bot/main.py`
- Bot uses Redis for both FSM state and LangGraph checkpointing
- Rate limiting is implemented at the middleware level
- All LLM interactions go through the graph-based conversation system
- When adding new LLM functionality, extend the existing graph structure rather than creating standalone handlers
- Use dependency injection patterns following the Clean Architecture approach

## Legacy Code

The `old/` directory contains the previous implementation that was migrated to Clean Architecture. Reference it for understanding the evolution but avoid using old patterns in new code.