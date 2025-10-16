# 🗺️ Codebase Tour

Детальный обзор кодовой базы за 20 минут.

## Структура проекта

```
systech-aidd-1/
├── src/                    # Весь код в одной папке (плоская структура)
│   ├── main.py             # Точка входа
│   ├── settings.py         # Конфигурация
│   ├── telegram_bot.py     # Telegram интеграция
│   ├── message_handler.py  # Координация обработки
│   ├── message_extractor.py # Извлечение данных
│   ├── openai_client.py    # LLM интеграция
│   ├── context_manager.py  # Управление контекстом
│   ├── memory_storage.py   # In-memory хранилище
│   ├── models.py           # Модели данных
│   ├── messages.py         # Текстовые константы
│   └── exceptions.py       # Кастомные исключения
│
├── tests/                  # Тесты (121 тест, 98% coverage)
│   ├── test_*.py           # Unit тесты
│   ├── test_integration.py # Интеграционные тесты
│   └── test_*_property.py  # Property-based тесты
│
├── docs/                   # Документация
│   ├── guides/             # Гайды (вы здесь)
│   ├── adrs/               # Архитектурные решения (ADR)
│   ├── reviews/            # Code reviews
│   ├── vision.md           # Техническое видение
│   ├── idea.md             # Идея проекта
│   ├── roadmap.md          # Roadmap со спринтами
│   └── tasklists/          # Тасклисты спринтов
│
├── examples/
│   └── prompts/            # Примеры системных промптов
│
├── logs/                   # Логи (создается автоматически)
│   └── YYYY-MM-DD.log
│
├── system_prompt.txt       # Системный промпт (роль ассистента)
├── .env                    # Секреты (не в git)
├── .env.example            # Пример конфигурации
├── pyproject.toml          # Зависимости и конфигурация
├── Makefile                # Команды для разработки
└── README.md               # Полная документация
```

## Точка входа: main.py

**Что делает:**
1. Настраивает логирование
2. Загружает конфигурацию (Settings)
3. Инициализирует компоненты через DI
4. Запускает бота

**Основные функции:**

### `setup_logging(log_level: str)`
Настраивает логирование в консоль и файл:
- Формат: `timestamp|module|level|message`
- Файлы: `logs/YYYY-MM-DD.log`
- Кодировка: UTF-8

### `async main()`
Точка входа приложения:
```python
settings = Settings()
openai_client = OpenAIClient(...)
context_manager = ContextManager(max_messages=10)
storage = MemoryStorage()
message_handler = MessageHandler(...)
bot = TelegramBot(...)
await bot.start()
```

**Где смотреть:** `src/main.py` (94 строки)

---

## Конфигурация: settings.py

**Роль:** Загрузка и валидация конфигурации

**Класс Settings:**
```python
class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # OpenRouter/LLM
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENAI_MODEL: str = "openai/gpt-3.5-turbo"

    # Logging
    LOG_LEVEL: str = "INFO"

    # System prompt
    SYSTEM_PROMPT_FILE: str = "system_prompt.txt"

    @property
    def system_prompt(self) -> str:
        # Загружает промпт из файла
```

**Особенности:**
- Использует pydantic для валидации
- Загружает `.env` автоматически
- Бросает ошибку если обязательные параметры отсутствуют
- Загружает системный промпт из файла

**Где смотреть:** `src/settings.py` (47 строк)

---

## Telegram интеграция: telegram_bot.py

**Роль:** Инициализация и запуск Telegram бота

**Класс TelegramBot:**
```python
class TelegramBot:
    def __init__(self, token: str, message_handler: MessageHandler):
        self._bot = Bot(token)
        self._dp = Dispatcher()
        self._message_handler = message_handler
        self._register_handlers()

    async def start(self):
        # Запускает polling
```

**Регистрирует handlers:**
- `/start` → `message_handler.handle_start_command()`
- `/help` → `message_handler.handle_help_command()`
- `/role` → `message_handler.handle_role_command()`
- `/reset` → `message_handler.handle_reset_command()`
- Текст → `message_handler.handle_text_message()`

**Где смотреть:** `src/telegram_bot.py` (64 строки)

---

## Координация: message_handler.py

**Роль:** Бизнес-логика обработки сообщений

**Класс MessageHandler:**

### Обработка команд
- `handle_start_command()` - регистрация пользователя, приветствие
- `handle_help_command()` - справка
- `handle_role_command()` - показать системный промпт
- `handle_reset_command()` - очистка истории

### Обработка текста
- `handle_text_message()` - основной flow:
  1. Извлечь данные (MessageExtractor)
  2. Получить/создать пользователя (MemoryStorage)
  3. Добавить сообщение в контекст (ContextManager)
  4. Получить контекст для LLM (ContextManager)
  5. Отправить запрос к LLM (OpenAIClient)
  6. Добавить ответ в контекст (ContextManager)
  7. Отправить ответ пользователю

### Обработка ошибок
```python
try:
    response = await self._openai_client.send_message(...)
except LLMTimeoutError:
    await message.answer(BotMessages.ERROR_TIMEOUT)
except LLMRateLimitError:
    await message.answer(BotMessages.ERROR_RATE_LIMIT)
# ... другие ошибки
```

**Где смотреть:** `src/message_handler.py` (168 строк)

---

## Извлечение данных: message_extractor.py

**Роль:** Извлечение данных из Telegram сообщений (DRY)

**Класс MessageContext (dataclass):**
```python
@dataclass
class MessageContext:
    user_id: int
    chat_id: int
    username: Optional[str]
    first_name: str
    text: str
```

**Класс MessageExtractor:**
```python
@staticmethod
def extract(message: TelegramMessage) -> MessageContext:
    # Извлекает все поля из Telegram сообщения
    return MessageContext(...)
```

**Зачем нужен:**
- Устраняет дублирование кода
- Единая точка извлечения данных
- Проще тестировать

**Где смотреть:** `src/message_extractor.py` (30 строк)

---

## LLM интеграция: openai_client.py

**Роль:** Взаимодействие с LLM через OpenRouter

**Класс OpenAIClient:**
```python
class OpenAIClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def send_message(self, messages: List[Message],
                          system_prompt: str) -> str:
        # Async обертка через run_in_executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._sync_send_message, messages, system_prompt)
        )

    def _sync_send_message(self, messages, system_prompt):
        # Синхронный вызов OpenAI API
        try:
            response = self._client.chat.completions.create(...)
            return response.choices[0].message.content
        except Timeout:
            raise LLMTimeoutError(...)
        except RateLimitError:
            raise LLMRateLimitError(...)
        # ... другие ошибки
```

**Особенности:**
- Синхронный OpenAI client в async обертке
- Обрабатывает все типы ошибок
- Бросает кастомные исключения

**Где смотреть:** `src/openai_client.py` (91 строка)

---

## Управление контекстом: context_manager.py

**Роль:** Управление историей диалога

**Класс ContextManager:**

### Основные методы
```python
def add_message(self, chat_id: int, role: str, content: str):
    # Добавляет сообщение в контекст
    # Ограничивает max_messages (10)

def get_context(self, chat_id: int) -> List[Message]:
    # Возвращает историю для LLM

def reset(self, chat_id: int):
    # Очищает контекст
```

**Логика:**
1. Получает conversation из storage
2. Добавляет новое сообщение
3. Обрезает до max_messages (FIFO)
4. Сохраняет обратно в storage

**Где смотреть:** `src/context_manager.py` (72 строки)

---

## Хранилище: memory_storage.py

**Роль:** In-memory хранилище данных

**Класс MemoryStorage:**

### Структура данных
```python
self._users: Dict[int, User] = {}
self._conversations: Dict[int, Conversation] = {}
```

### CRUD операции

**Пользователи:**
- `create_user()` - создать нового
- `get_user()` - получить по ID
- `update_user_activity()` - обновить last_activity

**Диалоги:**
- `get_conversation()` - получить по chat_id
- `save_conversation()` - сохранить/обновить
- `delete_conversation()` - удалить

**Метрики:**
- `get_total_users()` - количество пользователей
- `get_total_messages()` - количество сообщений

**Ограничения:**
- Данные в памяти (теряются при рестарте)
- Нет персистентности
- Нет транзакций

**Где смотреть:** `src/memory_storage.py` (113 строк)

---

## Модели данных: models.py

**Роль:** Dataclass модели для типизации

**User:**
```python
@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: str
    created_at: datetime
    last_activity: datetime
```

**Message:**
```python
@dataclass
class Message:
    role: str              # "user" или "assistant"
    content: str
    timestamp: datetime
```

**Conversation:**
```python
@dataclass
class Conversation:
    chat_id: int
    user_id: int
    messages: List[Message]
    context: str           # Системный промпт
    created_at: datetime
    updated_at: datetime
```

**Особенности:**
- Используют `@dataclass` для автогенерации `__init__`, `__repr__`
- Полная типизация
- Immutable where possible

**Где смотреть:** `src/models.py` (58 строк)

---

## Текстовые константы: messages.py

**Роль:** Все текстовые сообщения бота (DRY)

**Класс BotMessages:**
```python
class BotMessages:
    # Команды
    START = "Привет! 👋\n..."
    HELP = "Доступные команды:\n..."
    ROLE_INFO = "🎭 Моя текущая роль:\n\n{prompt}"
    RESET_SUCCESS = "История диалога очищена ✨"

    # Ошибки
    ERROR_TIMEOUT = "Извините, запрос занял слишком много времени ⏱️"
    ERROR_RATE_LIMIT = "Превышен лимит запросов 🚦"
    ERROR_CONNECTION = "Проблема с подключением к LLM API 🔌"
    ERROR_API = "Произошла ошибка при обращении к LLM API ⚠️"
    ERROR_UNEXPECTED = "Произошла непредвиденная ошибка 😔"
```

**Зачем:**
- Централизованное хранение текстов
- Легко изменить все сообщения
- Нет hardcode в коде
- Проще локализация (в будущем)

**Где смотреть:** `src/messages.py` (58 строк)

---

## Исключения: exceptions.py

**Роль:** Кастомные исключения для обработки ошибок

**Иерархия:**
```python
LLMError (базовый)
├── LLMConnectionError
├── LLMTimeoutError
├── LLMRateLimitError
└── LLMAPIError
```

**Использование:**
```python
# В OpenAIClient
raise LLMTimeoutError("Request timeout", original_error)

# В MessageHandler
except LLMTimeoutError as e:
    logger.error(f"llm_error|type=timeout|error={str(e)}")
    await message.answer(BotMessages.ERROR_TIMEOUT)
```

**Где смотреть:** `src/exceptions.py` (36 строк)

---

## Тесты

### Структура тестов

```
tests/
├── test_settings.py              # Settings (7 тестов)
├── test_messages.py              # BotMessages (21 тест)
├── test_message_extractor.py    # MessageExtractor (5 тестов)
├── test_exceptions.py            # Exceptions (6 тестов)
├── test_models.py                # Models (8 тестов)
├── test_memory_storage.py       # MemoryStorage (13 тестов)
├── test_context_manager.py      # ContextManager (11 тестов)
├── test_context_manager_property.py  # Property-based (7 тестов)
├── test_openai_client.py        # OpenAIClient (10 тестов)
├── test_message_handler.py      # MessageHandler (24 теста)
├── test_telegram_bot.py         # TelegramBot (9 тестов)
└── test_integration.py          # Integration (5 тестов)
```

**Итого:** 121 тест, 98% coverage

### Маркеры pytest
- `@pytest.mark.unit` - изолированное тестирование класса
- `@pytest.mark.integration` - полный flow
- `@pytest.mark.property` - property-based с Hypothesis

**Запуск:**
```bash
make test-unit         # Только unit
make test-integration  # Только integration
make test-property     # Только property-based
make test-cov          # Все с coverage
```

**Где смотреть:** `tests/` директория

---

## Конфигурационные файлы

### pyproject.toml
Управление зависимостями и конфигурация инструментов:
- **dependencies** - production зависимости
- **dev dependencies** - pytest, ruff, mypy, hypothesis
- **[tool.ruff]** - форматтер и линтер
- **[tool.mypy]** - strict mode типизация
- **[tool.pytest]** - маркеры, testpaths
- **[tool.coverage]** - требования покрытия (>=95%)

### Makefile
Команды для разработки:
```makefile
install      # Установить зависимости
run          # Запустить бота
test         # Запустить тесты
format       # Форматирование кода
lint         # Проверка линтером
type-check   # Проверка типов
quality      # Полная проверка
```

### .env
Секреты (не в git):
```bash
TELEGRAM_BOT_TOKEN=...
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-3.5-turbo
LOG_LEVEL=INFO
```

### system_prompt.txt
Роль ассистента (легко меняется):
```
Ты - универсальный помощник...
```

**Примеры:** `examples/prompts/` (technical, educational, creative)

---

## Документация

### docs/guides/
Гайды для онбординга (вы здесь)

### docs/adrs/
Architecture Decision Records:
- **ADR-001** - Dependency Injection
- **ADR-002** - OpenAI Client + OpenRouter
- **ADR-003** - Ollama локальный LLM
- **ADR-004** - Ruff + Mypy
- **ADR-005** - Hypothesis property-based testing

### docs/reviews/
Code reviews примеры

### docs/vision.md
Техническое видение проекта:
- Принципы архитектуры
- Технологии и стек
- Компоненты системы
- Модель данных

### docs/roadmap.md
Roadmap проекта со спринтами

### docs/tasklists/
Детальные планы разработки по спринтам:
- **tasklist-sp0.md** - План основной разработки (7 итераций, все завершены)
- **tasklist_tech_dept-sp0.md** - План устранения технического долга (4 итерации, все завершены)

---

## Где что искать?

**Точка входа приложения:**
→ `src/main.py`

**Бизнес-логика:**
→ `src/message_handler.py`

**Модели данных:**
→ `src/models.py`

**Текстовые сообщения:**
→ `src/messages.py`

**Обработка ошибок:**
→ `src/exceptions.py`

**Конфигурация:**
→ `src/settings.py`, `.env`

**Системный промпт:**
→ `system_prompt.txt`, `examples/prompts/`

**Тесты:**
→ `tests/`

**Документация:**
→ `docs/`, `README.md`

**Команды разработки:**
→ `Makefile`

**Архитектурные решения:**
→ `docs/adrs/`

---

## Что дальше?

✅ **Вы знаете где что находится**

Следующие шаги:
1. [Development Workflow](08-development-workflow.md) - процесс разработки
2. [Testing Guide](09-testing-guide.md) - тестирование

---

**Время выполнения: 20 минут**

