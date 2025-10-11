.PHONY: install run test clean setup install-dev test-cov format lint type-check quality

# Установка зависимостей и создание виртуального окружения
install:
	uv sync

# Установка в dev режиме (с тестовыми зависимостями)
install-dev:
	uv sync --all-extras

# Запуск бота в виртуальном окружении
run:
	uv run python src/main.py

# Запуск всех тестов
test:
	uv run pytest tests/ -v

# Запуск только unit-тестов
test-unit:
	uv run pytest tests/ -v -m unit

# Запуск только интеграционных тестов
test-integration:
	uv run pytest tests/ -v -m integration

# Запуск только property-based тестов
test-property:
	uv run pytest tests/ -v -m property

# Запуск всех тестов (альтернативное имя)
test-all: test

# Запуск тестов с покрытием
test-cov:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Форматирование кода с помощью ruff
format:
	uv run ruff format src/ tests/
	@echo "✅ Код отформатирован"

# Проверка кода линтером ruff
lint:
	uv run ruff check src/ tests/
	@echo "✅ Линтинг завершен"

# Проверка типов с помощью mypy
type-check:
	uv run mypy src/
	@echo "✅ Проверка типов завершена"

# Комплексная проверка качества
quality: format lint type-check test-cov
	@echo "✅ Все проверки качества пройдены"

# Очистка кэша и временных файлов
clean:
	rm -rf .pytest_cache __pycache__ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Первоначальная настройка проекта
setup:
	cp .env.example .env
	@echo "✅ Скопирован .env.example -> .env"
	@echo "⚠️  Не забудьте заполнить .env файл своими токенами!"
	uv sync --all-extras
	@echo "✅ Виртуальное окружение создано и зависимости установлены"

