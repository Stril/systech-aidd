# 🚀 Getting Started

Запуск проекта за 10 минут.

## Prerequisites

- **Python 3.11+**
- **uv** - менеджер пакетов Python

### Установка uv

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Шаг 1: Клонирование и установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd systech-aidd-1

# Установите зависимости
make setup
```

Команда `make setup` выполнит:
- Создание виртуального окружения через uv
- Установку всех зависимостей (production + dev)
- Копирование `.env.example` → `.env`

## Шаг 2: Настройка переменных окружения

Отредактируйте файл `.env`:

```bash
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenRouter API Key (получить на openrouter.ai)
OPENAI_API_KEY=your_openrouter_api_key_here

# OpenRouter Base URL (не изменять)
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# Модель LLM (можно изменить)
OPENAI_MODEL=openai/gpt-3.5-turbo

# Уровень логирования
LOG_LEVEL=INFO
```

### Как получить токены

**Telegram Bot Token:**
1. Откройте Telegram, найдите [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Следуйте инструкциям (имя и username бота)
4. Скопируйте токен в `.env`

**OpenRouter API Key:**
1. Зарегистрируйтесь на [openrouter.ai](https://openrouter.ai/)
2. Перейдите в раздел **API Keys**
3. Создайте новый ключ
4. Скопируйте в `.env`

## Шаг 3: Запуск бота

```bash
make run
```

Вы увидите:
```
2025-10-16 10:00:00|src.main|INFO|application|status=starting
2025-10-16 10:00:01|src.main|INFO|application|status=bot_starting
```

**Бот запущен!** ✅

## Шаг 4: Проверка работы

1. Откройте Telegram
2. Найдите вашего бота по username
3. Отправьте `/start`
4. Бот должен ответить приветствием

## Шаг 5: Запуск тестов (опционально)

```bash
# Запустить все тесты
make test

# Запустить с покрытием
make test-cov

# Полная проверка качества
make quality
```

Вы должны увидеть:
```
121 passed in ~15 seconds
coverage: 98%
```

## Troubleshooting

### Бот не запускается

**Проблема:** `Invalid token`
- Проверьте `TELEGRAM_BOT_TOKEN` в `.env`
- Убедитесь, что токен скопирован полностью

**Проблема:** `OpenAI API error`
- Проверьте `OPENAI_API_KEY` в `.env`
- Убедитесь, что на аккаунте OpenRouter есть баланс

**Проблема:** `uv: command not found`
- Установите uv (см. Prerequisites)
- Перезапустите терминал после установки

### Тесты падают

**Проблема:** `ModuleNotFoundError`
```bash
# Переустановите зависимости
make install-dev
```

### Логи не создаются

**Проблема:** Папка `logs/` не существует
- Папка создается автоматически при запуске
- Проверьте права на запись в директории проекта

## Что дальше?

✅ **Бот запущен и работает**

Следующие шаги:
1. [Quick Tour](02-quick-tour.md) - изучите команды и возможности
2. [Architecture Overview](03-architecture-overview.md) - поймите архитектуру
3. [Development Workflow](08-development-workflow.md) - начните разработку

---

**Время выполнения: 10 минут**

