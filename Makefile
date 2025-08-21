.PHONY: help install dev test lint format clean docker-build docker-run

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -e .
	pip install -e ".[dev]"

dev: ## Запустить в режиме разработки
	python apps/telegram_bot/main.py

test: ## Запустить тесты
	pytest

test-cov: ## Запустить тесты с покрытием
	pytest --cov=. --cov-report=html

lint: ## Проверить код линтерами
	black --check .
	isort --check-only .
	ruff check .
	mypy .

format: ## Отформатировать код
	black .
	isort .
	ruff check --fix .

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-build: ## Собрать Docker образ
	docker build -t booking-bot .

docker-run: ## Запустить в Docker
	docker-compose up -d

docker-stop: ## Остановить Docker контейнеры
	docker-compose down

migrate: ## Запустить миграции БД
	alembic upgrade head

migrate-create: ## Создать новую миграцию
	alembic revision --autogenerate -m "$(message)"

pre-commit: ## Установить pre-commit hooks
	pre-commit install
