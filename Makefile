.PHONY: install run test clean setup install-dev test-cov

# Установка зависимостей и создание виртуального окружения
install:
	uv sync

# Установка в dev режиме (с тестовыми зависимостями)
install-dev:
	uv sync --all-extras

# Запуск бота в виртуальном окружении
run:
	uv run python src/main.py

# Запуск тестов в виртуальном окружении
test:
	uv run pytest tests/ -v

# Запуск тестов с покрытием
test-cov:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

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

