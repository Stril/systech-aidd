# ADR-007: Использование SQLAlchemy ORM с Alembic для миграций

## Статус
Принято

## Контекст
В рамках спринта SP-1 необходимо выбрать подход к работе с SQLite базой данных (см. ADR-006). Нужно решить:
1. Использовать ли ORM (SQLAlchemy, Tortoise ORM) или прямой SQL
2. Какой инструмент использовать для миграций схемы БД

Характеристики проекта:
- **Async/await архитектура** - обязательна поддержка
- **Качество кода** - типизация, тестирование
- **Долгосрочная поддержка** - код должен легко поддерживаться
- **Масштабируемость** - возможность роста проекта
- **Стандарты Python** - использование проверенных решений

Анализ текущих операций с данными (`MemoryStorage`):
- `add_user(user)` - INSERT OR REPLACE
- `get_user(user_id)` - SELECT по первичному ключу
- `add_message_to_conversation(user_id, message)` - INSERT
- `get_conversation(user_id)` - SELECT с JOIN
- `clear_conversation(user_id)` - DELETE
- `get_metrics()` - простые COUNT/SUM агрегации

## Проблема
Необходимо выбрать подход к работе с БД:
1. **ORM vs прямой SQL** - что даст лучшую поддерживаемость?
2. **Инструмент миграций** - как управлять версиями схемы БД?
3. **Баланс между простотой и профессиональными стандартами**

## Варианты решения

### Вариант 1: SQLAlchemy + Alembic (принят)
Индустриальный стандарт ORM для Python с профессиональной системой миграций.

**Плюсы:**
- ✅ **Стандарт де-факто** для Python проектов
- ✅ **Async поддержка** через SQLAlchemy 2.0+
- ✅ **Автогенерация миграций** - Alembic создает миграции автоматически
- ✅ **Rollback миграций** - можно откатывать изменения
- ✅ **Типизация** - отличная поддержка mypy
- ✅ **Защита от SQL-инъекций** на уровне ORM
- ✅ **Валидация данных** на уровне моделей
- ✅ **Богатая экосистема** - множество расширений
- ✅ **Легкая миграция на PostgreSQL** в будущем
- ✅ **Query Builder** - избегаем ошибок в SQL
- ✅ **Relationships** - автоматическая работа с связями
- ✅ **Зрелость** - 15+ лет разработки, проверено временем

**Минусы:**
- ⚠️ Дополнительные зависимости (sqlalchemy, alembic, aiosqlite)
  - *Приемлемо*: Это стандартные инструменты
- ⚠️ Кривая обучения
  - *Решение*: Документация отличная, инвестиция окупается
- ⚠️ Абстракция над SQL
  - *Преимущество*: Защищает от ошибок

**Пример использования:**
```python
# Модель - чистая и типизированная
class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    message_count: Mapped[int] = mapped_column(default=0)

# Запрос - простой и безопасный
async with AsyncSession(engine) as session:
    result = await session.execute(
        select(User).where(User.user_id == 123)
    )
    user = result.scalar_one_or_none()

# Миграции - автогенерация
# alembic revision --autogenerate -m "Add users table"
# alembic upgrade head
```

### Вариант 2: Tortoise ORM + Aerich (отклонен)
Async-native ORM для Python, вдохновленная Django ORM.

**Плюсы:**
- Async из коробки
- Автогенерация миграций
- Проще SQLAlchemy
- Django-like API

**Минусы:**
- ❌ Менее зрелая чем SQLAlchemy
- ❌ Меньше сообщество и экосистема
- ❌ Хуже поддержка типизации (mypy)
- ❌ Не стандарт индустрии
- ❌ Меньше материалов для обучения

### Вариант 3: aiosqlite без ORM (отклонен)
Прямое использование SQL с async поддержкой.

**Плюсы:**
- Минимум зависимостей
- Полный контроль над SQL
- Максимальная производительность

**Минусы:**
- ❌ Ручное написание всех SQL запросов
- ❌ Ручное управление миграциями
- ❌ Риск SQL-инъекций при ошибках
- ❌ Нет валидации на уровне кода
- ❌ Сложнее поддерживать при росте проекта
- ❌ Больше boilerplate кода
- ❌ Ручное управление relationships
- ❌ Нет автогенерации миграций

## Решение
Принят **Вариант 1: SQLAlchemy 2.0+ с Alembic** как индустриальный стандарт.

### Обоснование

#### 1. Стандарт индустрии Python
SQLAlchemy - это **стандарт де-факто** для работы с БД в Python:
- Используется в Django (опционально), FastAPI, Flask
- Проверен в тысячах production проектов
- Активно поддерживается и развивается
- Огромное сообщество и множество материалов

#### 2. Отличная async поддержка (SQLAlchemy 2.0+)
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Async engine
engine = create_async_engine("sqlite+aiosqlite:///data/bot.db")

# Async операции
async with AsyncSession(engine) as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

#### 3. Автогенерация миграций с Alembic
```bash
# Изменили модели - автоматически создается миграция
alembic revision --autogenerate -m "Add message_count to users"

# Применяем миграции
alembic upgrade head

# Откатываем если нужно
alembic downgrade -1
```

**Alembic сам обнаруживает изменения:**
- Новые таблицы и колонки
- Удаленные таблицы и колонки
- Изменение типов
- Новые индексы и constraints

#### 4. Типизация и mypy
SQLAlchemy 2.0+ имеет отличную поддержку типов:
```python
# Mapped[] - полная типизация
class User(Base):
    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None]  # Опциональное поле
    created_at: Mapped[datetime]  # Обязательное поле

# mypy понимает типы
user = await session.get(User, 123)
# user: User | None - mypy знает это!
```

#### 5. Валидация и constraints на уровне ORM
```python
class Message(Base):
    __tablename__ = 'messages'

    role: Mapped[str] = mapped_column(String(20))

    @validates('role')
    def validate_role(self, key, value):
        if value not in ['user', 'assistant']:
            raise ValueError(f"Invalid role: {value}")
        return value
```

#### 6. Защита от SQL-инъекций
ORM автоматически экранирует параметры:
```python
# Безопасно - параметры экранируются автоматически
result = await session.execute(
    select(User).where(User.username == user_input)
)

# Вместо уязвимого:
# f"SELECT * FROM users WHERE username = '{user_input}'"
```

#### 7. Relationships и lazy loading
```python
class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True)

    # Автоматическая связь
    messages: Mapped[list["Message"]] = relationship(back_populates="user")

class Message(Base):
    __tablename__ = 'messages'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))

    user: Mapped["User"] = relationship(back_populates="messages")

# Простое использование
user = await session.get(User, 123)
messages = user.messages  # Автоматический JOIN!
```

#### 8. Легкая миграция на PostgreSQL
Когда проект вырастет:
```python
# SQLite
engine = create_async_engine("sqlite+aiosqlite:///bot.db")

# PostgreSQL - меняется только URL!
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/bot"
)

# Код моделей и запросов остается тем же!
```

#### 9. Меньше boilerplate кода
```python
# С SQLAlchemy
user = User(user_id=123, username="test", created_at=datetime.now())
session.add(user)
await session.commit()

# Без ORM - больше кода
async with aiosqlite.connect(db_path) as db:
    await db.execute(
        "INSERT INTO users (user_id, username, first_name, created_at, message_count) VALUES (?, ?, ?, ?, ?)",
        (user.user_id, user.username, user.first_name,
         user.created_at.isoformat(), user.message_count)
    )
    await db.commit()
```

#### 10. Профессиональные стандарты
Использование SQLAlchemy показывает профессиональный подход:
- Код понятен любому Python разработчику
- Легко найти разработчиков, знающих SQLAlchemy
- Множество примеров и best practices
- Интеграция со всеми популярными фреймворками

## Последствия

### Положительные
- ✅ **Индустриальный стандарт** - проверенное решение
- ✅ **Автогенерация миграций** - экономия времени
- ✅ **Типизация и mypy** - меньше багов
- ✅ **Защита от SQL-инъекций** - безопасность из коробки
- ✅ **Валидация данных** - на уровне моделей
- ✅ **Легкая миграция на PostgreSQL** - изменяется только URL
- ✅ **Меньше кода** - ORM убирает boilerplate
- ✅ **Relationships** - автоматическая работа со связями
- ✅ **Rollback миграций** - можно откатывать
- ✅ **Богатая экосистема** - расширения и инструменты
- ✅ **Отличная документация** - легко учиться
- ✅ **Async из коробки** - SQLAlchemy 2.0+

### Отрицательные
- ⚠️ Дополнительные зависимости
  - *Приемлемо*: Это стандартные, проверенные библиотеки
  - `sqlalchemy[asyncio]`, `alembic`, `aiosqlite` - всего 3 пакета
- ⚠️ Кривая обучения
  - *Инвестиция*: Знание SQLAlchemy полезно для любого Python проекта
  - *Документация*: Отличная официальная документация
- ⚠️ Небольшой overhead производительности
  - *Не критично*: Для нашей нагрузки незаметно
  - *Компенсируется*: Меньше багов, быстрее разработка

### Нейтральные
- 📝 Абстракция над SQL (можно писать raw SQL если нужно)
- 📝 Больше возможностей, чем нужно сейчас (но пригодится при росте)

## Реализация

### Структура проекта
```
systech-aidd-1/
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── data/
│   └── bot.db
├── src/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # Base model class
│   │   ├── models.py        # SQLAlchemy models
│   │   └── session.py       # Engine и session factory
│   ├── sqlite_storage.py    # Реализация Storage с SQLAlchemy
│   └── models.py            # Dataclasses (для бизнес-логики)
└── pyproject.toml
```

### Зависимости
```toml
[dependencies]
sqlalchemy = { version = "^2.0.0", extras = ["asyncio"] }
alembic = "^1.12.0"
aiosqlite = "^0.19.0"
```

### SQLAlchemy модели

**src/db/base.py:**
```python
"""SQLAlchemy base model"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all models"""
    pass
```

**src/db/models.py:**
```python
"""SQLAlchemy models"""
from datetime import datetime
from sqlalchemy import String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class User(Base):
    """User model"""
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    message_count: Mapped[int] = mapped_column(default=0)

    # Relationship
    conversation: Mapped["Conversation"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Conversation(Base):
    """Conversation model"""
    __tablename__ = 'conversations'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="conversation")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    """Message model"""
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id', ondelete='CASCADE')
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationship
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='check_role'),
    )
```

**src/db/session.py:**
```python
"""Database session management"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from src.settings import Settings


def create_engine(settings: Settings):
    """Create async engine"""
    database_url = f"sqlite+aiosqlite:///{settings.database_path}"

    return create_async_engine(
        database_url,
        echo=settings.log_level == "DEBUG",
        future=True,
    )


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """Create session factory"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

### SQLiteStorage с SQLAlchemy

**src/sqlite_storage.py:**
```python
"""SQLite storage with SQLAlchemy ORM"""
import logging
from typing import Optional
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import User as DBUser, Conversation as DBConversation, Message as DBMessage
from src.models import User, Message, Conversation

logger = logging.getLogger(__name__)


class SQLiteStorage:
    """SQLite storage using SQLAlchemy ORM"""

    def __init__(self, session_factory) -> None:
        """Initialize storage with session factory"""
        self.session_factory = session_factory
        logger.info("sqlite_storage|status=initialized")

    # User operations

    async def add_user(self, user: User) -> None:
        """Add or update user"""
        async with self.session_factory() as session:
            db_user = await session.get(DBUser, user.user_id)

            if db_user:
                # Update existing
                db_user.username = user.username
                db_user.first_name = user.first_name
                db_user.message_count = user.message_count
            else:
                # Create new
                db_user = DBUser(
                    user_id=user.user_id,
                    username=user.username,
                    first_name=user.first_name,
                    created_at=user.created_at,
                    message_count=user.message_count
                )
                session.add(db_user)

            await session.commit()
            logger.info(f"sqlite_storage|user_added|user_id={user.user_id}")

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        async with self.session_factory() as session:
            db_user = await session.get(DBUser, user_id)

            if db_user:
                return User(
                    user_id=db_user.user_id,
                    username=db_user.username,
                    first_name=db_user.first_name,
                    created_at=db_user.created_at,
                    message_count=db_user.message_count
                )
            return None

    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(DBUser).where(DBUser.user_id == user_id)
            )
            return result.scalar_one_or_none() is not None

    # Conversation operations

    async def add_message_to_conversation(
        self, user_id: int, message: Message
    ) -> None:
        """Add message to user's conversation"""
        async with self.session_factory() as session:
            # Get or create conversation
            conversation = await session.get(DBConversation, user_id)
            if not conversation:
                conversation = DBConversation(
                    user_id=user_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(conversation)
            else:
                conversation.updated_at = datetime.now()

            # Add message
            db_message = DBMessage(
                user_id=message.user_id,
                role=message.role,
                content=message.content,
                timestamp=message.timestamp
            )
            session.add(db_message)

            await session.commit()

    async def get_conversation(self, user_id: int) -> Optional[Conversation]:
        """Get user's conversation with messages"""
        async with self.session_factory() as session:
            # Load conversation with messages eagerly
            result = await session.execute(
                select(DBConversation)
                .where(DBConversation.user_id == user_id)
                .options(selectinload(DBConversation.messages))
            )
            db_conv = result.scalar_one_or_none()

            if not db_conv:
                return None

            # Convert to business model
            messages = [
                Message(
                    user_id=msg.user_id,
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp
                )
                for msg in db_conv.messages
            ]

            return Conversation(
                user_id=db_conv.user_id,
                messages=messages,
                created_at=db_conv.created_at,
                updated_at=db_conv.updated_at
            )

    async def clear_conversation(self, user_id: int) -> None:
        """Clear user's conversation"""
        async with self.session_factory() as session:
            # Delete all messages for user
            result = await session.execute(
                select(DBMessage).where(DBMessage.user_id == user_id)
            )
            messages = result.scalars().all()

            for msg in messages:
                await session.delete(msg)

            await session.commit()
            logger.info(f"sqlite_storage|conversation_cleared|user_id={user_id}")

    # Metrics

    async def get_total_users(self) -> int:
        """Get total number of users"""
        async with self.session_factory() as session:
            result = await session.execute(select(func.count(DBUser.user_id)))
            return result.scalar() or 0

    async def get_total_messages(self) -> int:
        """Get total number of messages"""
        async with self.session_factory() as session:
            result = await session.execute(select(func.count(DBMessage.id)))
            return result.scalar() or 0
```

### Alembic конфигурация

**alembic.ini:**
```ini
[alembic]
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s
prepend_sys_path = .

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

**alembic/env.py:**
```python
"""Alembic environment configuration"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from src.db.base import Base
from src.db.models import User, Conversation, Message  # noqa - import all models
from src.settings import Settings

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata для автогенерации
target_metadata = Base.metadata

# Database URL from settings
settings = Settings()
config.set_main_option(
    "sqlalchemy.url",
    f"sqlite+aiosqlite:///{settings.database_path}"
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

### Использование миграций

```bash
# Инициализация (уже сделано)
alembic init alembic

# Создание первой миграции (автогенерация)
alembic revision --autogenerate -m "Initial schema"

# Применение миграций
alembic upgrade head

# Просмотр истории
alembic history

# Откат на одну версию назад
alembic downgrade -1

# Откат всех миграций
alembic downgrade base
```

### Инициализация в main.py

```python
# src/main.py
from src.db.base import Base
from src.db.session import create_engine, create_session_factory
from src.sqlite_storage import SQLiteStorage


async def create_app():
    settings = Settings()

    # Создаем engine и session factory
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    # Создаем таблицы (для dev, в prod используем alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # SQLite storage с SQLAlchemy
    storage = SQLiteStorage(session_factory)

    # Остальное без изменений (Dependency Injection!)
    openai_client = OpenAIClient(...)
    context_manager = ContextManager(storage, ...)
    message_handler = MessageHandler(openai_client, context_manager, storage)
    telegram_bot = TelegramBot(settings.telegram_bot_token, message_handler)

    return telegram_bot
```

### Тестирование

```python
# tests/test_sqlite_storage.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from src.db.base import Base
from src.db.session import create_session_factory
from src.sqlite_storage import SQLiteStorage
from src.models import User


@pytest.fixture
async def storage():
    """In-memory SQLite для тестов"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = create_session_factory(engine)
    storage = SQLiteStorage(session_factory)

    yield storage

    await engine.dispose()


@pytest.mark.asyncio
async def test_add_and_get_user(storage):
    user = User(
        user_id=123,
        username="test_user",
        first_name="Test",
        created_at=datetime.now(),
        message_count=0
    )

    await storage.add_user(user)
    retrieved = await storage.get_user(123)

    assert retrieved is not None
    assert retrieved.user_id == 123
    assert retrieved.username == "test_user"
```

## Сравнительная таблица

| Критерий | SQLAlchemy + Alembic | Tortoise + Aerich | aiosqlite + SQL |
|----------|---------------------|-------------------|-----------------|
| **Стандарт индустрии** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Async support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Типизация (mypy)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Автомиграции** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| **Rollback миграций** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| **Экосистема** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Документация** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Миграция на PostgreSQL** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Защита от SQL-инъекций** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Простота** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Для production** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## Альтернативы, которые были рассмотрены
- **Tortoise ORM + Aerich** - отклонен, менее зрелый чем SQLAlchemy
- **aiosqlite без ORM** - отклонен, больше кода и меньше безопасности
- **Django ORM** - отклонен, требует Django framework
- **Peewee ORM** - отклонен, устаревший, нет async
- **SQLModel** - отклонен, менее зрелый чем SQLAlchemy

## Связанные решения
- ADR-006: Выбор SQLite как СУБД
- ADR-001: Dependency Injection (позволит легко менять реализацию)
- ADR-004: Ruff + Mypy (SQLAlchemy отлично работает с mypy)

## Метрики успеха
- ✅ Автогенерация миграций работает
- ✅ Rollback миграций работает
- ✅ Типизация проходит mypy strict mode
- ✅ Coverage тестами >= 80%
- ✅ Время разработки Storage < 6 часов
- ✅ Код понятен Python разработчикам

## Миграция на PostgreSQL в будущем
```python
# SQLite
DATABASE_URL = "sqlite+aiosqlite:///data/bot.db"

# PostgreSQL - ТОЛЬКО URL меняется!
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/bot"

# Весь код моделей и запросов - БЕЗ ИЗМЕНЕНИЙ! ✅
```

---
**Дата:** 2025-10-16
**Автор:** Команда разработки
**Статус:** Принято

