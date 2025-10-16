<!-- 4194cca7-9fe3-45c2-8f77-dd15c90991e5 1c661abf-a8c1-44cc-87ad-af7aa1bd32b7 -->
# Plan: Sprint S1 - Персистентное хранение данных

## Обзор

Переход от in-memory хранения к SQLite БД с SQLAlchemy ORM и Alembic. Реализация soft delete (deleted_at) для всех сущностей и добавление метаданных к сообщениям (created_at, content_length). Пользователь может вести несколько диалогов.

## Ключевые решения

- **БД**: SQLite (простота, без Docker для БД)
- **ORM**: SQLAlchemy (async) + aiosqlite
- **Миграции**: Alembic
- **Soft delete**: поле `deleted_at` для User, Conversation, Message
- **Новые поля Message**: `content_length: int`, явный `created_at`
- **Множественные диалоги**: пользователь может иметь несколько диалогов
- **Docker**: для контейнеризации приложения с volume для БД
- **user_id как PK**: Telegram user_id является первичным ключом таблицы users

## Схема базы данных

### Таблица: users

Хранит пользователей Telegram бота.

**Поля:**

- `user_id` - INTEGER PRIMARY KEY - Telegram user ID (первичный ключ, БЕЗ AUTOINCREMENT)
- `username` - VARCHAR(255) NULLABLE - Telegram username
- `first_name` - VARCHAR(255) NULLABLE - Имя пользователя
- `created_at` - TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `message_count` - INTEGER NOT NULL DEFAULT 0 - Счетчик сообщений
- `deleted_at` - TIMESTAMP NULLABLE - Soft delete

**Индексы:**

- `idx_users_deleted_at` - на `deleted_at` (фильтрация активных записей)

**Constraints:**

- `message_count >= 0`

### Таблица: conversations

Хранит диалоги пользователей (пользователь может иметь несколько диалогов).

**Поля:**

- `id` - INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id` - INTEGER NOT NULL - FK to users.user_id
- `created_at` - TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `updated_at` - TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `deleted_at` - TIMESTAMP NULLABLE - Soft delete

**Индексы:**

- `idx_conversations_user_id` - на `user_id` (поиск диалогов пользователя, БЕЗ UNIQUE)
- `idx_conversations_deleted_at` - на `deleted_at` (фильтрация активных)

**Constraints:**

- `user_id` FOREIGN KEY REFERENCES users(user_id) ON DELETE CASCADE

### Таблица: messages

Хранит историю сообщений в диалогах.

**Поля:**

- `id` - INTEGER PRIMARY KEY AUTOINCREMENT
- `conversation_id` - INTEGER NOT NULL
- `user_id` - INTEGER NOT NULL - FK to users.user_id
- `role` - VARCHAR(20) NOT NULL - "user" или "assistant"
- `content` - TEXT NOT NULL - Содержимое сообщения
- `content_length` - INTEGER NOT NULL - Длина сообщения в символах
- `created_at` - TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `deleted_at` - TIMESTAMP NULLABLE - Soft delete

**Индексы:**

- `idx_messages_conversation_id` - на `conversation_id` (получение сообщений диалога)
- `idx_messages_user_id` - на `user_id` (получение сообщений пользователя)
- `idx_messages_created_at` - на `created_at` (сортировка по времени)
- `idx_messages_deleted_at` - на `deleted_at` (фильтрация активных)
- `idx_messages_composite` - COMPOSITE на `(conversation_id, deleted_at, created_at)` (оптимизация частых запросов)

**Constraints:**

- `user_id` FOREIGN KEY REFERENCES users(user_id) ON DELETE CASCADE

### Связи между таблицами

- **users → conversations**: ONE-TO-MANY (один пользователь - много диалогов)
- **users → messages**: ONE-TO-MANY (один пользователь - много сообщений) через FK
- **conversations → messages**: ONE-TO-MANY (один диалог - много сообщений)

### Стратегия Soft Delete

Все таблицы поддерживают soft delete через поле `deleted_at`:

- `deleted_at IS NULL` - запись активна
- `deleted_at IS NOT NULL` - запись удалена

**Все SELECT запросы** фильтруют: `WHERE deleted_at IS NULL`
**При "удалении"**: `UPDATE table SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?`

## Этапы реализации

### 1. Зависимости и конфигурация

- Добавить в `pyproject.toml`: `sqlalchemy[asyncio]>=2.0`, `aiosqlite>=0.19`, `alembic>=1.12`
- Добавить в `Settings`: `DATABASE_URL` (default: `sqlite+aiosqlite:///data/bot.db`)
- Создать директорию `data/` с `.gitkeep`, добавить `data/bot.db` в `.gitignore`

### 2. Обновить модели данных

Файл: `src/models.py`

- **User**: оставить `user_id: int` как есть (это будет PK в БД), добавить `deleted_at: datetime | None = None`
- **Message**: добавить `id: int | None = None`, переименовать `timestamp` → `created_at`, добавить `content_length: int`, `deleted_at: datetime | None = None`
- **Conversation**: добавить `id: int | None = None`, `deleted_at: datetime | None = None`

### 3. Создать SQLAlchemy модели

**Новый файл: `src/database_base.py`**

- Базовый класс `Base` от `DeclarativeBase`
- Общие настройки для всех моделей

**Новый файл: `src/user_db.py`**

- Класс `UserDB(Base)` - `user_id` как PRIMARY KEY (БЕЗ AUTOINCREMENT)
- Методы конвертации: `to_domain()` для преобразования DB модели в domain модель
- Методы конвертации: `from_domain()` для преобразования domain модели в DB модель

**Новый файл: `src/conversation_db.py`**

- Класс `ConversationDB(Base)` с полями и индексами (БЕЗ UNIQUE на user_id)
- Методы конвертации: `to_domain()` и `from_domain()`

**Новый файл: `src/message_db.py`**

- Класс `MessageDB(Base)` с полями, индексами и FK на users(user_id)
- Методы конвертации: `to_domain()` и `from_domain()`

**Примечание**: Следуя конвенции "1 класс = 1 файл", каждая модель в отдельном файле.

### 4. Настроить Alembic

- Инициализировать: `alembic init migrations`
- Настроить `alembic.ini`: sqlalchemy.url = `sqlite:///data/bot.db` (синхронный для alembic CLI)
- Настроить `migrations/env.py`:
- Импорт `database_base.Base`
- Импорт всех моделей: `user_db.UserDB`, `conversation_db.ConversationDB`, `message_db.MessageDB`
- Настройка async поддержки для run_migrations_online
- target_metadata = Base.metadata
- Создать первую миграцию: `alembic revision --autogenerate -m "Initial schema with soft delete"`
- Применить: `alembic upgrade head`

### 5. Реализовать SQLiteStorage

Новый файл: `src/sqlite_storage.py`

Класс `SQLiteStorage` с интерфейсом аналогичным `MemoryStorage`:

- `__init__(database_url: str)` - инициализация async engine
- Методы User: `add_user()`, `get_user()`, `user_exists()`, `get_all_users()`, `increment_user_message_count()`
- Методы Conversation: `add_message_to_conversation()`, `get_conversation()`, `clear_conversation()` (soft delete через deleted_at)
- Методы Metrics: `get_total_users()`, `get_total_messages()`, `get_metrics()`
- Приватные хелперы для конвертации DB ↔ Domain моделей
- Все SELECT с фильтром `deleted_at.is_(None)`
- Async context manager или метод `close()` для graceful shutdown
- Поддержка множественных диалогов на пользователя

### 6. Обновить тесты

Новый файл: `tests/test_sqlite_storage.py`

- Использовать in-memory SQLite: `sqlite+aiosqlite:///:memory:`
- Fixture `async_db_session` для создания таблиц перед каждым тестом
- **Маркер тестов**: `@pytest.mark.integration` (работа с реальной БД, даже in-memory)
- Скопировать структуру тестов из `test_memory_storage.py`
- Добавить тесты для soft delete:
- `test_soft_delete_user()` - проверка что удаленный user не возвращается
- `test_soft_delete_conversation()` - clear_conversation делает soft delete
- `test_soft_delete_messages()` - сообщения не видны после удаления
- Тесты для множественных диалогов пользователя
- Coverage >= 80%

### 7. Docker окружение

Создать файлы для контейнеризации:

**Dockerfile:**

- Multi-stage build: builder (установка зависимостей) + runtime (минимальный образ)
- Base image: python:3.11-slim
- Копирование только необходимых файлов
- WORKDIR /app
- Создание директории /app/data для БД
- CMD для запуска через uv

**docker-compose.yml:**

- Сервис `bot` с build context
- Environment variables из `.env`
- Volume для персистентности: `./data:/app/data`
- Restart policy: unless-stopped
- Networks для изоляции

**.dockerignore:**

- Исключить `.git`, `__pycache__`, `.pytest_cache`, `data/`, `logs/`

Проверить: `docker-compose up --build` → бот запускается, БД создается в `./data/bot.db`

### 8. Интеграция в приложение

Файл: `src/main.py`

- Заменить инициализацию `MemoryStorage()` → `SQLiteStorage(settings.DATABASE_URL)`
- Добавить async startup: применение миграций или проверка схемы
- Добавить graceful shutdown: `await storage.close()` для закрытия соединений
- Логирование при инициализации БД

### 9. Документация

**ADR-007**: `docs/adrs/adr-007-sqlalchemy-alembic.md`

- Контекст: выбор между raw SQL, SQLAlchemy, Tortoise ORM
- Решение: SQLAlchemy + Alembic
- Обоснование: стандарт индустрии, богатая экосистема, отличная async поддержка
- Последствия: больше зависимостей, но стандартное решение

**README.md** - добавить секции:

- База данных (SQLite, миграции через Alembic)
- Команды миграций: `alembic upgrade head`, `alembic revision --autogenerate`
- Бэкапы: `cp data/bot.db backups/`
- Docker: запуск через `docker-compose up`

**docs/guides/04-codebase-tour.md:**

- Описание SQLAlchemy моделей: `src/database_base.py`, `src/user_db.py`, `src/conversation_db.py`, `src/message_db.py`
- Описание `src/sqlite_storage.py` (storage реализация)
- Описание миграций и Alembic

## Файлы для создания

- `src/database_base.py` - базовый класс для SQLAlchemy моделей
- `src/user_db.py` - модель UserDB
- `src/conversation_db.py` - модель ConversationDB
- `src/message_db.py` - модель MessageDB
- `src/sqlite_storage.py` - реализация storage для SQLite
- `tests/test_sqlite_storage.py` - тесты storage (маркер @pytest.mark.integration)
- `data/.gitkeep` - пустая директория для БД
- `Dockerfile` - контейнер приложения
- `docker-compose.yml` - оркестрация
- `.dockerignore` - исключения для Docker
- `migrations/` - Alembic миграции (через CLI)
- `docs/adrs/adr-007-sqlalchemy-alembic.md` - ADR

## Файлы для изменения

- `pyproject.toml` - добавить зависимости
- `src/models.py` - добавить поля для БД (user_id остается как есть - PK)
- `src/settings.py` - добавить DATABASE_URL
- `src/main.py` - заменить MemoryStorage на SQLiteStorage
- `.gitignore` - добавить `data/bot.db`, `data/*.db`
- `README.md` - секция про БД и Docker
- `docs/guides/04-codebase-tour.md` - новые компоненты

## Принципы реализации

- **KISS**: простая реализация без излишних абстракций
- **DRY**: переиспользование кода конвертации моделей (хелперы)
- **1 класс = 1 файл**: строго соблюдаем
- **Async/await**: все операции БД асинхронные через aiosqlite
- **Soft delete**: все "удаления" через `deleted_at = datetime.now()`
- **Tests first**: сначала тесты, потом реализация (TDD где возможно)
- **Гибкость**: пользователь может иметь несколько диалогов
- **Natural keys**: используем Telegram user_id как естественный первичный ключ
- **Referential integrity**: FK в messages на users для целостности данных
- **Quality checks**: все изменения проверяются через `make quality` перед коммитом

### To-dos

- [ ] Добавить зависимости: sqlalchemy[asyncio], aiosqlite, alembic в pyproject.toml
- [ ] Обновить src/models.py: добавить id, deleted_at, content_length, created_at
- [ ] Создать src/database_base.py с базовым классом Base
- [ ] Создать src/user_db.py с моделью UserDB и методами конвертации
- [ ] Создать src/conversation_db.py с моделью ConversationDB и методами конвертации
- [ ] Создать src/message_db.py с моделью MessageDB и методами конвертации
- [ ] Добавить DATABASE_URL в src/settings.py
- [ ] Настроить Alembic: init, конфиг, импорт всех моделей в env.py, создать первую миграцию
- [ ] Реализовать src/sqlite_storage.py с async методами и soft delete
- [ ] Написать tests/test_sqlite_storage.py с маркером @pytest.mark.integration и покрытием >=80%
- [ ] Создать Dockerfile, docker-compose.yml, .dockerignore для контейнеризации
- [ ] Интегрировать SQLiteStorage в src/main.py, заменить MemoryStorage
- [ ] Создать ADR-007, обновить README и guides с информацией про БД и Docker
- [ ] Запустить make quality, проверить coverage, исправить ошибки