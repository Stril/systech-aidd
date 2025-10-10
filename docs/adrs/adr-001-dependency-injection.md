# ADR-001: Использование Dependency Injection

## Статус
Принято

## Контекст
При разработке LLM-ассистента в виде Telegram-бота необходимо определить подход к управлению зависимостями между компонентами системы. Проект включает следующие основные компоненты:

- `TelegramBot` - основной класс бота
- `MessageHandler` - обработка входящих сообщений
- `OpenAIClient` - взаимодействие с LLM
- `ContextManager` - управление контекстом диалога
- `MemoryStorage` - хранение данных в памяти
- `Settings` - конфигурация приложения

## Проблема
Необходимо решить, как организовать взаимодействие между компонентами системы, чтобы обеспечить:
- Слабую связанность компонентов
- Возможность тестирования
- Гибкость в изменении реализаций
- Соответствие принципам SOLID

## Варианты решения

### Вариант 1: Жесткая связанность (отклонен)
```python
class MessageHandler:
    def __init__(self):
        self.openai_client = OpenAIClient()  # Жесткая связанность
        self.memory_storage = MemoryStorage()
```

**Плюсы:**
- Простота реализации

**Минусы:**
- Невозможность тестирования
- Жесткая связанность
- Сложность изменения реализаций

### Вариант 2: Service Locator (отклонен)
```python
class MessageHandler:
    def __init__(self):
        self.openai_client = ServiceLocator.get(OpenAIClient)
```

**Плюсы:**
- Централизованное управление зависимостями

**Минусы:**
- Скрытые зависимости
- Сложность отладки
- Нарушение принципа "Explicit is better than implicit"

### Вариант 3: Dependency Injection через конструктор (принят)
```python
class MessageHandler:
    def __init__(self, openai_client: OpenAIClient, 
                 context_manager: ContextManager,
                 memory_storage: MemoryStorage):
        self.openai_client = openai_client
        self.context_manager = context_manager
        self.memory_storage = memory_storage
```

**Плюсы:**
- Явные зависимости
- Легкое тестирование
- Слабая связанность
- Соответствие принципам SOLID
- Простота реализации

**Минусы:**
- Небольшое увеличение сложности инициализации

## Решение
Принят **Вариант 3: Dependency Injection через конструктор**.

### Обоснование
1. **Соответствие принципам проекта:**
   - KISS (Keep It Simple, Stupid) - простая реализация
   - "Explicit is better than implicit" - явные зависимости
   - Single Responsibility - каждый класс отвечает за свою задачу

2. **Технические преимущества:**
   - Возможность unit-тестирования с mock-объектами
   - Легкая замена реализаций (например, MemoryStorage → DatabaseStorage)
   - Соблюдение Dependency Inversion Principle

3. **Простота реализации:**
   - Не требует дополнительных библиотек
   - Понятная инициализация в main.py
   - Минимальная сложность

## Последствия

### Положительные
- ✅ Слабая связанность компонентов
- ✅ Возможность тестирования
- ✅ Гибкость в изменении реализаций
- ✅ Соответствие принципам SOLID
- ✅ Простота понимания и поддержки

### Отрицательные
- ⚠️ Небольшое увеличение сложности инициализации
- ⚠️ Необходимость передавать зависимости через конструкторы

### Нейтральные
- 📝 Централизованная инициализация в main.py
- 📝 Явное объявление зависимостей в каждом классе

## Реализация

### Структура инициализации в main.py:
```python
def create_app():
    # Инициализация в правильном порядке
    settings = Settings()
    memory_storage = MemoryStorage()
    openai_client = OpenAIClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        model=settings.model
    )
    context_manager = ContextManager(memory_storage)
    message_handler = MessageHandler(
        openai_client=openai_client,
        context_manager=context_manager,
        memory_storage=memory_storage
    )
    telegram_bot = TelegramBot(
        bot_token=settings.bot_token,
        message_handler=message_handler
    )
    return telegram_bot
```

### Пример тестирования:
```python
def test_message_handler():
    # Создание mock-объектов
    mock_client = Mock(spec=OpenAIClient)
    mock_context = Mock(spec=ContextManager)
    mock_storage = Mock(spec=MemoryStorage)
    
    # Инициализация с mock-зависимостями
    handler = MessageHandler(mock_client, mock_context, mock_storage)
    
    # Тестирование логики без реальных зависимостей
    assert handler is not None
```

## Альтернативы, которые были рассмотрены
- Использование DI-контейнера (например, dependency-injector) - отклонено как избыточное для проекта
- Паттерн Factory - отклонен в пользу простой инициализации
- Singleton для глобальных сервисов - отклонен как нарушающий принципы тестирования

## Связанные решения
- ADR-002: Использование OpenAI Client с OpenRouter
- ADR-003: Поддержка локального Ollama через OpenAI Client
- ADR-004: Подход к обработке ошибок (планируется)

---
**Дата:** 2024-01-15  
**Автор:** Команда разработки  
**Статус:** Принято
