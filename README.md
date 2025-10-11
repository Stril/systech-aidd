# 🤖 LLM Telegram Bot Assistant

Telegram-бот с интеграцией LLM для помощи в различных задачах. Разработан с принципом KISS (Keep It Simple, Stupid) и следует строгой архитектуре 1 класс = 1 файл.

## 📋 Возможности

- ✅ Базовый Telegram бот с поддержкой команд
- ✅ Интеграция с LLM через OpenRouter (GPT-4, Claude, Llama и др.)
- ✅ Обработка текстовых сообщений и генерация ответов
- ✅ Управление контекстом диалога (помнит последние 10 сообщений)
- ✅ Команда `/reset` для очистки истории диалога
- ✅ In-memory хранилище для пользователей и диалогов
- ✅ Отслеживание метрик (количество пользователей, сообщений)
- ✅ Логирование в файлы по дням (logs/YYYY-MM-DD.log)
- ✅ Graceful обработка ошибок LLM API (таймауты, лимиты, сетевые ошибки)
- ✅ Понятные сообщения пользователю при ошибках
- ✅ Простая архитектура с разделением ответственности
- ✅ Конфигурация через переменные окружения
- ✅ Структурированное логирование
- ✅ Unit-тесты для основных компонентов

## 🛠️ Технологии

- **Python 3.11+** - основной язык разработки
- **uv** - управление зависимостями и виртуальными окружениями
- **aiogram 3.x** - Telegram Bot API с polling
- **openai** - клиент для работы с LLM через OpenRouter
- **pydantic** - валидация конфигурации
- **pytest** - тестирование

## 🚀 Быстрый старт

### 1. Предварительные требования

Убедитесь, что у вас установлены:
- Python 3.11 или новее
- [uv](https://github.com/astral-sh/uv) - менеджер пакетов Python

Установка uv:
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Первоначальная настройка

```bash
# Создание виртуального окружения и установка зависимостей
make setup
```

Эта команда:
- Скопирует `.env.example` в `.env` (если возможно)
- Создаст виртуальное окружение через `uv`
- Установит все зависимости

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта (если не был создан автоматически):

```bash
# .env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openrouter_api_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-3.5-turbo
LOG_LEVEL=INFO
```

**Как получить токены:**

1. **Telegram Bot Token:**
   - Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
   - Отправьте команду `/newbot`
   - Следуйте инструкциям для создания бота
   - Скопируйте полученный токен в `.env` файл

2. **OpenRouter API Key:**
   - Зарегистрируйтесь на [OpenRouter.ai](https://openrouter.ai/)
   - Перейдите в раздел API Keys
   - Создайте новый ключ и скопируйте в `.env` файл

### 4. Запуск бота

```bash
# Запуск в виртуальном окружении
make run
```

### 5. Запуск тестов

```bash
# Тесты также запускаются в виртуальном окружении
make test

# С покрытием кода
make test-cov
```

## 📁 Структура проекта

```
systech-aidd-1/
├── src/
│   ├── __init__.py
│   ├── settings.py           # Settings класс (конфигурация)
│   ├── telegram_bot.py       # TelegramBot класс
│   ├── message_handler.py    # MessageHandler для команд
│   ├── openai_client.py      # OpenAIClient для LLM
│   ├── context_manager.py    # ContextManager для истории диалогов
│   ├── memory_storage.py     # MemoryStorage для хранения данных
│   ├── models.py             # Модели данных (User, Message, Conversation)
│   ├── exceptions.py         # Кастомные исключения для обработки ошибок
│   └── main.py               # Точка входа
├── tests/
│   ├── __init__.py
│   ├── test_settings.py      # Тесты Settings
│   ├── test_message_handler.py  # Тесты MessageHandler
│   ├── test_openai_client.py    # Тесты OpenAIClient
│   ├── test_context_manager.py  # Тесты ContextManager
│   ├── test_memory_storage.py   # Тесты MemoryStorage
│   └── test_exceptions.py       # Тесты кастомных исключений
├── docs/
│   ├── idea.md               # Идея проекта
│   ├── vision.md             # Техническое видение
│   └── tasklist.md           # План разработки
├── logs/                     # Логи по дням (создается автоматически)
├── .env.example              # Пример конфигурации
├── .gitignore
├── pyproject.toml            # Зависимости проекта
├── Makefile                  # Команды для разработки
└── README.md
```

## 🎯 Доступные команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку по командам
- `/reset` - Очистить историю диалога
- **Текстовые сообщения** - Отправьте любое текстовое сообщение, и бот ответит через LLM с учетом контекста

## 🔧 Makefile команды

```bash
make install      # Установить зависимости
make install-dev  # Установить зависимости + dev зависимости
make setup        # Первоначальная настройка проекта
make run          # Запустить бота
make test         # Запустить тесты
make test-cov     # Запустить тесты с покрытием
make clean        # Очистить временные файлы
```

## 📊 Принципы разработки

- **KISS** - максимальная простота, никакого оверинжиниринга
- **1 класс = 1 файл** - строгое соблюдение
- **Single Responsibility** - каждый класс отвечает за одну задачу
- **Dependency Injection** - простая инъекция зависимостей
- **Fail Fast** - быстрое обнаружение ошибок

## 🧪 Тестирование

Проект использует pytest для unit-тестирования. Тесты покрывают:
- Валидацию конфигурации (Settings)
- Обработку команд (MessageHandler)
- Взаимодействие с LLM (OpenAIClient)
- Управление контекстом диалога (ContextManager)
- Хранение данных в памяти (MemoryStorage)
- Модели данных (User, Message, Conversation)
- Обработку ошибок LLM API (Connection, Timeout, RateLimit, API errors)
- Кастомные исключения
- Обработку текстовых сообщений

Запуск тестов:
```bash
make test
```

**Статистика тестов:** 64 теста, 100% pass rate

## 📝 Логирование

Логи выводятся одновременно в консоль и в файлы по дням в структурированном формате с разделителем `|`:

**Файлы логов:**
- `logs/2025-10-10.log` - логи за конкретный день
- Автоматическое создание новых файлов каждый день
- Кодировка UTF-8 для корректного отображения кириллицы

**Формат логов:**
```
2025-10-10 10:30:00|src.telegram_bot|INFO|telegram_bot|status=initialized
2025-10-10 10:30:01|src.message_handler|INFO|user_command|user_id=123|command=start
2025-10-10 10:30:05|src.openai_client|ERROR|llm_error|type=timeout|error=Request timeout
```

## 🗺️ Roadmap

- [x] **Итерация #1**: Базовая инфраструктура + Telegram-бот
- [x] **Итерация #2**: Интеграция с LLM (OpenRouter)
- [x] **Итерация #3**: Управление контекстом диалога
- [x] **Итерация #4**: In-memory хранилище
- [x] **Итерация #5**: Логирование в файлы и обработка ошибок
- [ ] **Итерация #6**: Финальная полировка

Подробный план см. в [docs/tasklist.md](docs/tasklist.md)

## 📖 Документация

- [idea.md](docs/idea.md) - Исходная идея проекта
- [vision.md](docs/vision.md) - Техническое видение и архитектура
- [tasklist.md](docs/tasklist.md) - Детальный план разработки по итерациям

## 🤝 Вклад в разработку

Проект следует строгим принципам разработки, описанным в документации. При внесении изменений:
1. Следуйте принципу "1 класс = 1 файл"
2. Используйте type hints
3. Пишите unit-тесты
4. Придерживайтесь KISS принципа

## 📄 Лицензия

MIT License

---

**Версия**: 0.5.0  
**Статус**: В разработке (Итерация #5 завершена)

