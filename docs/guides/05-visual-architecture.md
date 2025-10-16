# 05. Визуальная архитектура проекта

> **Навигация**: [← Назад к обзору кодовой базы](04-codebase-tour.md) | [Главная](README.md) | [Далее: Процесс разработки →](08-development-workflow.md)

---

Этот документ представляет визуализацию проекта LLM-ассистента с различных точек зрения, используя разнообразные диаграммы для понимания архитектуры, потоков данных, взаимодействий и сценариев использования.

## Содержание

1. [Компонентная архитектура](#1-компонентная-архитектура)
2. [Поток данных](#2-поток-данных)
3. [Последовательность взаимодействий](#3-последовательность-взаимодействий)
4. [Диаграмма классов](#4-диаграмма-классов)
5. [Машина состояний](#5-машина-состояний)
6. [Путь пользователя](#6-путь-пользователя)
7. [Развертывание](#7-развертывание)
8. [Обработка ошибок](#8-обработка-ошибок)

---

## 1. Компонентная архитектура

Высокоуровневое представление компонентов системы и их взаимодействия:

```mermaid
graph TB
    subgraph External["🌐 Внешние системы"]
        TG[Telegram API]
        OR[OpenRouter/LLM API]
    end

    subgraph Core["⚙️ Ядро приложения"]
        TB[TelegramBot<br/>📱 Entry Point]
        MH[MessageHandler<br/>🎯 Координатор]

        subgraph Services["Сервисы"]
            OC[OpenAIClient<br/>🤖 LLM Client]
            CM[ContextManager<br/>💬 Контекст]
            MS[MemoryStorage<br/>💾 Хранилище]
        end

        subgraph Utils["Утилиты"]
            ME[MessageExtractor<br/>📝 Извлечение данных]
            BM[BotMessages<br/>📢 Константы]
            EX[Exceptions<br/>⚠️ Исключения]
        end

        subgraph Config["Конфигурация"]
            ST[Settings<br/>⚙️ Настройки]
            MD[Models<br/>📊 Модели данных]
        end
    end

    TG -->|polling| TB
    TB -->|delegate| MH
    MH -->|extract| ME
    MH -->|messages| BM
    MH -->|llm request| OC
    MH -->|context ops| CM
    MH -->|storage ops| MS
    OC -->|API call| OR
    CM -->|persist| MS
    MH -->|handle errors| EX
    TB -.->|config| ST
    MH -.->|models| MD

    style TB fill:#FF6B6B,stroke:#C92A2A,stroke-width:3px,color:#fff
    style MH fill:#4ECDC4,stroke:#0D7377,stroke-width:3px,color:#fff
    style OC fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style CM fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style MS fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style ME fill:#A8DADC,stroke:#457B9D,stroke-width:2px,color:#000
    style BM fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style ST fill:#B4A7D6,stroke:#6A4C93,stroke-width:2px,color:#fff
    style MD fill:#DDA15E,stroke:#BC6C25,stroke-width:2px,color:#fff
    style EX fill:#EF476F,stroke:#C71F37,stroke-width:2px,color:#fff
    style TG fill:#2A9D8F,stroke:#264653,stroke-width:2px,color:#fff
    style OR fill:#E9C46A,stroke:#E76F51,stroke-width:2px,color:#000
```

### Описание компонентов:

- **TelegramBot** - точка входа, управление polling и регистрация handlers
- **MessageHandler** - главный координатор обработки сообщений
- **OpenAIClient** - асинхронное взаимодействие с LLM API
- **ContextManager** - управление историей диалога в памяти
- **MemoryStorage** - хранение пользователей и сообщений
- **MessageExtractor** - извлечение данных из Telegram сообщений
- **BotMessages** - константы текстовых сообщений
- **Settings** - конфигурация и валидация параметров
- **Models** - модели данных (User, Message, Conversation)
- **Exceptions** - кастомные исключения для LLM ошибок

---

## 2. Поток данных

Визуализация потока данных от получения сообщения до отправки ответа:

```mermaid
flowchart LR
    User([👤 Пользователь])

    subgraph Input["📥 Получение"]
        TG_IN[Telegram API]
        BOT[TelegramBot]
    end

    subgraph Process["⚙️ Обработка"]
        EXTRACT[MessageExtractor<br/>📝 Извлечение]
        HANDLER[MessageHandler<br/>🎯 Координация]

        subgraph Context["💭 Управление контекстом"]
            CTX_GET[Получить историю]
            CTX_ADD[Добавить сообщение]
        end

        subgraph Storage["💾 Хранилище"]
            SAVE_USER[Сохранить<br/>пользователя]
            SAVE_MSG[Сохранить<br/>сообщение]
        end

        LLM[OpenAIClient<br/>🤖 LLM Request]
    end

    subgraph Output["📤 Отправка"]
        RESPONSE[Ответ LLM]
        TG_OUT[Telegram API]
    end

    User -->|текст| TG_IN
    TG_IN -->|Message| BOT
    BOT -->|Message| HANDLER
    HANDLER -->|Message| EXTRACT
    EXTRACT -->|MessageContext| HANDLER
    HANDLER -->|user_id| SAVE_USER
    HANDLER -->|user_id| CTX_GET
    CTX_GET -->|messages[]| HANDLER
    HANDLER -->|messages + prompt| LLM
    LLM -->|response| HANDLER
    HANDLER -->|user_id, response| CTX_ADD
    HANDLER -->|message| SAVE_MSG
    HANDLER -->|response| RESPONSE
    RESPONSE -->|text| TG_OUT
    TG_OUT -->|ответ| User

    style User fill:#FF6B6B,stroke:#C92A2A,stroke-width:3px,color:#fff
    style BOT fill:#4ECDC4,stroke:#0D7377,stroke-width:2px,color:#fff
    style HANDLER fill:#FFD93D,stroke:#F49D1A,stroke-width:3px,color:#000
    style EXTRACT fill:#A8DADC,stroke:#457B9D,stroke-width:2px,color:#000
    style LLM fill:#E9C46A,stroke:#E76F51,stroke-width:2px,color:#000
    style CTX_GET fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style CTX_ADD fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style SAVE_USER fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style SAVE_MSG fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style RESPONSE fill:#B4A7D6,stroke:#6A4C93,stroke-width:2px,color:#fff
    style TG_IN fill:#2A9D8F,stroke:#264653,stroke-width:2px,color:#fff
    style TG_OUT fill:#2A9D8F,stroke:#264653,stroke-width:2px,color:#fff
```

### Ключевые этапы потока:

1. **Получение** - Telegram API → TelegramBot → MessageHandler
2. **Извлечение** - MessageExtractor создает MessageContext
3. **Контекст** - ContextManager предоставляет историю диалога
4. **LLM** - OpenAIClient отправляет запрос к AI модели
5. **Сохранение** - Обновление контекста и хранилища
6. **Отправка** - Ответ пользователю через Telegram API

---

## 3. Последовательность взаимодействий

Детальная последовательность обработки текстового сообщения:

```mermaid
sequenceDiagram
    actor U as 👤 User
    participant TG as Telegram API
    participant TB as TelegramBot
    participant MH as MessageHandler
    participant ME as MessageExtractor
    participant CM as ContextManager
    participant MS as MemoryStorage
    participant OC as OpenAIClient
    participant LLM as 🤖 LLM API

    U->>TG: Отправить сообщение
    TG->>TB: Message event
    TB->>MH: handle_text_message(message)

    rect rgba(168, 218, 220, 0.3)
        note over MH,ME: 📝 Извлечение данных
        MH->>ME: extract(message)
        ME-->>MH: MessageContext
    end

    rect rgba(107, 203, 119, 0.3)
        note over MH,MS: 💾 Работа с хранилищем
        MH->>MS: add_user(user)
        MS-->>MH: ✓
        MH->>CM: add_message(user_id, "user", text)
        CM->>MS: persist context
        MS-->>CM: ✓
        CM-->>MH: ✓
        MH->>CM: get_context(user_id)
        CM->>MS: load context
        MS-->>CM: messages[]
        CM-->>MH: messages[]
    end

    rect rgba(255, 217, 61, 0.3)
        note over MH,LLM: 🤖 LLM запрос
        MH->>OC: send_message(messages, prompt)
        OC->>LLM: POST /chat/completions
        LLM-->>OC: response
        OC-->>MH: response_text
    end

    rect rgba(149, 225, 211, 0.3)
        note over MH,MS: 💾 Сохранение ответа
        MH->>CM: add_message(user_id, "assistant", response)
        CM->>MS: persist response
        MS-->>CM: ✓
        CM-->>MH: ✓
        MH->>MS: add_message_to_conversation(user_id, msg)
        MS-->>MH: ✓
    end

    MH->>TB: answer(response)
    TB->>TG: Send response
    TG->>U: Ответ бота
```

### Этапы взаимодействия:

1. **Получение сообщения** - от пользователя через Telegram API
2. **Извлечение данных** - MessageExtractor создает контекст
3. **Управление пользователем** - создание/обновление в MemoryStorage
4. **Получение истории** - ContextManager → MemoryStorage
5. **LLM запрос** - OpenAIClient → LLM API (async)
6. **Сохранение ответа** - обновление контекста и хранилища
7. **Отправка ответа** - пользователю через Telegram API

---

## 4. Диаграмма классов

Структура классов и их отношения:

```mermaid
classDiagram
    class TelegramBot {
        -Bot _bot
        -Dispatcher _dp
        -MessageHandler _message_handler
        +__init__(token, message_handler)
        +start() async
        -_register_handlers()
    }

    class MessageHandler {
        -OpenAIClient _openai_client
        -str _system_prompt
        -ContextManager _context_manager
        -MemoryStorage _storage
        +handle_start(message) async
        +handle_help(message) async
        +handle_text_message(message) async
        +handle_reset(message) async
        +handle_role(message) async
    }

    class OpenAIClient {
        -AsyncOpenAI _client
        -str _model
        -ThreadPoolExecutor _executor
        +send_message(messages, system_prompt) async str
        -_sync_send_message(messages, system_prompt) str
    }

    class ContextManager {
        -dict~int, list~ _contexts
        -int _max_messages
        +add_message(user_id, role, content)
        +get_context(user_id) list
        +reset_context(user_id)
        -_trim_context(user_id)
    }

    class MemoryStorage {
        -dict~int, User~ _users
        -dict~int, Conversation~ _conversations
        +add_user(user)
        +get_user(user_id) User|None
        +user_exists(user_id) bool
        +add_message_to_conversation(user_id, message)
        +get_conversation(user_id) Conversation|None
        +clear_conversation(user_id)
    }

    class MessageExtractor {
        <<utility>>
        +extract(message)$ MessageContext
    }

    class BotMessages {
        <<constants>>
        +WELCOME$ str
        +HELP$ str
        +ERROR_CONNECTION$ str
        +ERROR_TIMEOUT$ str
        +RESET_SUCCESS$ str
        +ROLE_INFO$ str
    }

    class Settings {
        +str TELEGRAM_BOT_TOKEN
        +str OPENAI_API_KEY
        +str OPENAI_BASE_URL
        +str OPENAI_MODEL
        +str SYSTEM_PROMPT_FILE
        +int MAX_CONTEXT_MESSAGES
        +load_system_prompt() str
    }

    class User {
        <<dataclass>>
        +int user_id
        +str|None username
        +str first_name
        +datetime created_at
        +int message_count
    }

    class Message {
        <<dataclass>>
        +int user_id
        +str role
        +str content
        +datetime timestamp
    }

    class MessageContext {
        <<dataclass>>
        +int user_id
        +int chat_id
        +str username
        +str first_name
        +str text
        +datetime timestamp
    }

    class Conversation {
        <<dataclass>>
        +int chat_id
        +int user_id
        +list~Message~ messages
        +datetime created_at
        +datetime updated_at
    }

    %% Relationships
    TelegramBot --> MessageHandler : uses
    MessageHandler --> OpenAIClient : uses
    MessageHandler --> ContextManager : uses
    MessageHandler --> MemoryStorage : uses
    MessageHandler --> MessageExtractor : uses
    MessageHandler --> BotMessages : uses
    MemoryStorage --> User : stores
    MemoryStorage --> Conversation : stores
    Conversation --> Message : contains
    MessageExtractor --> MessageContext : creates
    Settings ..> TelegramBot : configures
    Settings ..> MessageHandler : configures
    Settings ..> OpenAIClient : configures
    Settings ..> ContextManager : configures

    style TelegramBot fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
    style MessageHandler fill:#4ECDC4,stroke:#0D7377,stroke-width:2px,color:#fff
    style OpenAIClient fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style ContextManager fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style MemoryStorage fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style MessageExtractor fill:#A8DADC,stroke:#457B9D,stroke-width:2px,color:#000
    style BotMessages fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style Settings fill:#B4A7D6,stroke:#6A4C93,stroke-width:2px,color:#fff
    style User fill:#DDA15E,stroke:#BC6C25,stroke-width:2px,color:#fff
    style Message fill:#DDA15E,stroke:#BC6C25,stroke-width:2px,color:#fff
    style MessageContext fill:#DDA15E,stroke:#BC6C25,stroke-width:2px,color:#fff
    style Conversation fill:#DDA15E,stroke:#BC6C25,stroke-width:2px,color:#fff
```

### Ключевые аспекты архитектуры классов:

- **Dependency Injection** - все зависимости передаются через конструктор
- **Single Responsibility** - каждый класс отвечает за одну задачу
- **1 класс = 1 файл** - строгое соблюдение принципа
- **Dataclasses** - для моделей данных (User, Message, Conversation)
- **Utility classes** - статические методы (MessageExtractor)
- **Constants classes** - для текстовых сообщений (BotMessages)

---

## 5. Машина состояний

Состояния контекста диалога пользователя:

```mermaid
stateDiagram-v2
    [*] --> NoContext: Новый пользователь

    NoContext --> EmptyContext: /start
    EmptyContext --> ActiveContext: Первое сообщение

    ActiveContext --> ActiveContext: Новое сообщение
    ActiveContext --> FullContext: Достигнут лимит (10 сообщений)

    FullContext --> FullContext: Новое сообщение<br/>(старые удаляются)

    ActiveContext --> EmptyContext: /reset
    FullContext --> EmptyContext: /reset
    EmptyContext --> [*]: Завершение сессии

    note right of NoContext
        Пользователь еще не<br/>
        зарегистрирован
    end note

    note right of EmptyContext
        Пользователь зарегистрирован,<br/>
        но контекст пуст
    end note

    note right of ActiveContext
        Активный диалог,<br/>
        контекст < 10 сообщений
    end note

    note right of FullContext
        Полный контекст,<br/>
        FIFO удаление старых
    end note

    style NoContext fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style EmptyContext fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style ActiveContext fill:#6BCB77,stroke:#2D6A4F,stroke-width:3px,color:#fff
    style FullContext fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
```

### Описание состояний:

- **NoContext** - пользователь не существует в системе
- **EmptyContext** - пользователь зарегистрирован, но история пуста
- **ActiveContext** - активный диалог с историей < 10 сообщений
- **FullContext** - полный контекст, новые сообщения вытесняют старые (FIFO)

### Триггеры переходов:

- `/start` - регистрация пользователя
- Текстовое сообщение - добавление в контекст
- `/reset` - очистка истории
- Достижение лимита - переход в режим FIFO

---

## 6. Путь пользователя

Визуализация пользовательских сценариев:

```mermaid
journey
    title Путь пользователя в LLM-ассистенте
    section Первое знакомство
      Открыть бота: 5: User
      Отправить /start: 5: User
      Прочитать приветствие: 4: User
      Отправить /help: 4: User
      Изучить команды: 4: User
    section Первый диалог
      Задать вопрос: 5: User
      Увидеть typing...: 3: User, Bot
      Получить ответ: 5: User, Bot
      Уточнить вопрос: 5: User
      Получить ответ с контекстом: 5: User, Bot
    section Работа с контекстом
      Продолжить диалог: 5: User, Bot
      Накопить историю: 4: User, Bot
      Переключить тему: 3: User
      Отправить /reset: 4: User
      Начать новую тему: 5: User, Bot
    section Проверка роли
      Отправить /role: 4: User
      Увидеть системный промпт: 4: User
      Понять возможности: 4: User
    section Обработка ошибок
      Задать вопрос: 5: User
      Получить ошибку API: 1: User, Bot
      Увидеть дружественное сообщение: 3: User
      Повторить попытку: 4: User
      Получить успешный ответ: 5: User, Bot
```

### Основные сценарии:

1. **Онбординг** - `/start`, `/help`, знакомство с ботом
2. **Диалог** - текстовые сообщения, контекстные ответы
3. **Управление контекстом** - `/reset` для новой темы
4. **Проверка роли** - `/role` для понимания возможностей
5. **Обработка ошибок** - graceful degradation при проблемах с API

---

## 7. Развертывание

Архитектура развертывания и зависимости:

```mermaid
graph TB
    subgraph Hosting["☁️ Хостинг"]
        subgraph Server["🖥️ Сервер"]
            subgraph Runtime["Python Runtime"]
                APP[main.py<br/>🚀 Entry Point]
            end

            subgraph Memory["💾 RAM"]
                USERS[(Users<br/>Dict)]
                CONV[(Conversations<br/>Dict)]
                CTX[(Contexts<br/>Dict)]
            end

            subgraph FileSystem["📁 Файловая система"]
                ENV[.env<br/>⚙️ Config]
                PROMPT[system_prompt.txt<br/>📝 Промпт]
                LOGS[logs/<br/>📋 Логи по дням]
            end
        end
    end

    subgraph External["🌐 Внешние сервисы"]
        TG_API[Telegram Bot API<br/>🤖 Polling]
        OR_API[OpenRouter API<br/>🧠 LLM Provider]
    end

    subgraph Dev["👨‍💻 Разработка"]
        UV[uv<br/>📦 Package Manager]
        MAKE[Makefile<br/>🛠️ Build Tool]
        TESTS[pytest<br/>✅ Testing]
        QUALITY[ruff + mypy<br/>🔍 Quality]
    end

    APP -->|polling| TG_API
    APP -->|API calls| OR_API
    APP -->|read| ENV
    APP -->|load| PROMPT
    APP -->|write| LOGS
    APP -->|store| USERS
    APP -->|store| CONV
    APP -->|store| CTX

    UV -.->|install deps| APP
    MAKE -.->|build & run| APP
    TESTS -.->|validate| APP
    QUALITY -.->|check| APP

    style APP fill:#FF6B6B,stroke:#C92A2A,stroke-width:3px,color:#fff
    style USERS fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style CONV fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style CTX fill:#95E1D3,stroke:#38A3A5,stroke-width:2px,color:#000
    style ENV fill:#B4A7D6,stroke:#6A4C93,stroke-width:2px,color:#fff
    style PROMPT fill:#DDA15E,stroke:#BC6C25,stroke-width:2px,color:#fff
    style LOGS fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style TG_API fill:#2A9D8F,stroke:#264653,stroke-width:2px,color:#fff
    style OR_API fill:#E9C46A,stroke:#E76F51,stroke-width:2px,color:#000
    style UV fill:#A8DADC,stroke:#457B9D,stroke-width:2px,color:#000
    style MAKE fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style TESTS fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style QUALITY fill:#4ECDC4,stroke:#0D7377,stroke-width:2px,color:#fff
```

### Компоненты развертывания:

**Runtime:**
- Python 3.11+ с asyncio
- Единая точка входа `main.py`

**In-Memory Storage:**
- Users - словарь пользователей
- Conversations - история диалогов
- Contexts - контекст для LLM

**File System:**
- `.env` - конфигурация (токены, API keys)
- `system_prompt.txt` - роль ассистента
- `logs/` - структурированные логи по дням

**External Services:**
- Telegram Bot API (polling режим)
- OpenRouter API (LLM провайдер)

**Development Tools:**
- `uv` - управление зависимостями
- `make` - автоматизация задач
- `pytest` - тестирование (98%+ coverage)
- `ruff + mypy` - качество кода

---

## 8. Обработка ошибок

Поток обработки ошибок и recovery сценарии:

```mermaid
flowchart TD
    START[Получено сообщение]

    START --> EXTRACT{Извлечение<br/>данных}
    EXTRACT -->|✓| CONTEXT{Получение<br/>контекста}
    EXTRACT -->|✗| ERR_EXTRACT[Ошибка валидации]

    CONTEXT -->|✓| LLM{LLM запрос}
    CONTEXT -->|✗| ERR_CONTEXT[Ошибка контекста]

    LLM -->|✓| SAVE{Сохранение<br/>ответа}
    LLM -->|Connection Error| ERR_CONN[LLMConnectionError]
    LLM -->|Timeout| ERR_TIMEOUT[LLMTimeoutError]
    LLM -->|Rate Limit| ERR_RATE[LLMRateLimitError]
    LLM -->|API Error| ERR_API[LLMAPIError]
    LLM -->|Other Error| ERR_LLM[LLMError]

    SAVE -->|✓| SEND[Отправка ответа]
    SAVE -->|✗| ERR_SAVE[Ошибка сохранения]

    ERR_EXTRACT --> LOG_EXTRACT[Логирование]
    ERR_CONTEXT --> LOG_CONTEXT[Логирование]
    ERR_CONN --> LOG_CONN[Логирование]
    ERR_TIMEOUT --> LOG_TIMEOUT[Логирование]
    ERR_RATE --> LOG_RATE[Логирование]
    ERR_API --> LOG_API[Логирование]
    ERR_LLM --> LOG_LLM[Логирование]
    ERR_SAVE --> LOG_SAVE[Логирование]

    LOG_EXTRACT --> MSG_EXTRACT[Сообщение пользователю:<br/>Некорректные данные]
    LOG_CONTEXT --> MSG_CONTEXT[Сообщение пользователю:<br/>Ошибка контекста]
    LOG_CONN --> MSG_CONN[Сообщение пользователю:<br/>Проблемы с подключением]
    LOG_TIMEOUT --> MSG_TIMEOUT[Сообщение пользователю:<br/>Превышен таймаут]
    LOG_RATE --> MSG_RATE[Сообщение пользователю:<br/>Превышен лимит запросов]
    LOG_API --> MSG_API[Сообщение пользователю:<br/>Ошибка API]
    LOG_LLM --> MSG_LLM[Сообщение пользователю:<br/>Ошибка LLM]
    LOG_SAVE --> MSG_SAVE[Сообщение пользователю:<br/>Ошибка сохранения]

    SEND --> END[Завершено]
    MSG_EXTRACT --> END
    MSG_CONTEXT --> END
    MSG_CONN --> END
    MSG_TIMEOUT --> END
    MSG_RATE --> END
    MSG_API --> END
    MSG_LLM --> END
    MSG_SAVE --> END

    style START fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style END fill:#6BCB77,stroke:#2D6A4F,stroke-width:2px,color:#fff
    style SEND fill:#4ECDC4,stroke:#0D7377,stroke-width:2px,color:#fff

    style ERR_EXTRACT fill:#EF476F,stroke:#C71F37,stroke-width:2px,color:#fff
    style ERR_CONTEXT fill:#EF476F,stroke:#C71F37,stroke-width:2px,color:#fff
    style ERR_CONN fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
    style ERR_TIMEOUT fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
    style ERR_RATE fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
    style ERR_API fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
    style ERR_LLM fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px,color:#fff
    style ERR_SAVE fill:#EF476F,stroke:#C71F37,stroke-width:2px,color:#fff

    style LOG_EXTRACT fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_CONTEXT fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_CONN fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_TIMEOUT fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_RATE fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_API fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_LLM fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000
    style LOG_SAVE fill:#F4A261,stroke:#E76F51,stroke-width:2px,color:#000

    style MSG_EXTRACT fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_CONTEXT fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_CONN fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_TIMEOUT fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_RATE fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_API fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_LLM fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
    style MSG_SAVE fill:#FFD93D,stroke:#F49D1A,stroke-width:2px,color:#000
```

### Типы ошибок и обработка:

**LLM Ошибки:**
- `LLMConnectionError` - проблемы с подключением к API
- `LLMTimeoutError` - превышен таймаут запроса
- `LLMRateLimitError` - превышен лимит запросов
- `LLMAPIError` - общая ошибка API
- `LLMError` - базовый класс для всех LLM ошибок

**Принципы обработки:**
1. **Graceful degradation** - система продолжает работать
2. **Локальное логирование** - все ошибки записываются в лог
3. **Дружественные сообщения** - понятные уведомления пользователю
4. **Fail fast** - быстрое обнаружение проблем
5. **Re-raise** - пробрасывание для обработки на верхнем уровне

---

## Заключение

Эти диаграммы представляют различные аспекты архитектуры LLM-ассистента:

- **Компонентная архитектура** - структура и взаимодействие компонентов
- **Поток данных** - путь сообщения от пользователя к ответу
- **Последовательность** - детальное взаимодействие между компонентами
- **Классы** - объектно-ориентированная структура
- **Состояния** - управление контекстом диалога
- **User Journey** - пользовательский опыт
- **Развертывание** - инфраструктура и зависимости
- **Ошибки** - обработка исключительных ситуаций

### Ключевые принципы архитектуры:

✅ **KISS** - максимальная простота
✅ **SOLID** - правильное разделение ответственности
✅ **DRY** - избегание дублирования кода
✅ **Async/Await** - неблокирующие операции
✅ **Fail Fast** - быстрое обнаружение ошибок
✅ **In-Memory** - хранение данных в RAM
✅ **1 класс = 1 файл** - понятная структура

---

> **Навигация**: [← Назад к обзору кодовой базы](04-codebase-tour.md) | [Главная](README.md) | [Далее: Процесс разработки →](08-development-workflow.md)

