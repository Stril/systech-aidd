# ADR-005: Использование Hypothesis для Property-Based Testing

## Статус
Предлагается к принятию

## Контекст
При разработке LLM-ассистента в виде Telegram-бота необходимо обеспечить надежность критичных компонентов системы. Проект включает компоненты с важными инвариантами:

- `ContextManager` - контекст никогда не должен превышать `max_messages`
- `MemoryStorage` - данные должны сохраняться корректно при любых операциях
- Обработка сообщений - корректность при различных входных данных
- Валидация данных - проверка граничных условий

## Проблема
Традиционное тестирование с конкретными примерами имеет ограничения:
- Не покрывает все возможные крайние случаи
- Требует явного написания тестов для каждого сценария
- Трудно предусмотреть все комбинации входных данных
- Граничные условия часто упускаются
- Сложно тестировать инварианты системы

## Варианты решения

### Вариант 1: Только традиционные unit-тесты (отклонен)
```python
def test_context_manager_add_message():
    cm = ContextManager(max_messages=3)
    cm.add_message({"role": "user", "content": "test"})
    assert len(cm.get_context()) == 1

def test_context_manager_max_messages():
    cm = ContextManager(max_messages=3)
    for i in range(5):
        cm.add_message({"role": "user", "content": f"msg{i}"})
    assert len(cm.get_context()) == 3
```

**Плюсы:**
- Простота написания
- Явные ожидаемые результаты
- Быстрое выполнение

**Минусы:**
- Проверяют только конкретные случаи
- Не находят неожиданные крайние случаи
- Требуют явного перечисления всех сценариев
- Легко упустить важные граничные условия

### Вариант 2: Hypothesis для Property-Based Testing (принят)
```python
from hypothesis import given
from hypothesis.strategies import lists, text, integers

@given(lists(text(), min_size=0, max_size=100))
def test_context_never_exceeds_max(messages):
    """Инвариант: контекст никогда не превышает max_messages"""
    cm = ContextManager(max_messages=10)
    for msg in messages:
        cm.add_message({"role": "user", "content": msg})
    assert len(cm.get_context()) <= 10
```

**Плюсы:**
- Автоматическая генерация тестовых данных
- Проверка инвариантов на сотнях примеров
- Находит неожиданные крайние случаи
- Автоматическое упрощение найденных багов (shrinking)
- Высокое покрытие при меньшем количестве кода

**Минусы:**
- Немного медленнее традиционных тестов
- Требует изменения мышления (свойства vs примеры)

### Вариант 3: Комбинация обоих подходов (принят как стратегия)
```python
# Традиционные тесты для конкретных сценариев
def test_empty_context():
    assert len(ContextManager(max_messages=10).get_context()) == 0

# Property-based тесты для инвариантов
@given(lists(text(), max_size=100))
def test_context_invariant(messages):
    # Проверка свойств на множестве примеров
    pass
```

## Решение
Принят **Вариант 3: Комбинация традиционных тестов и Hypothesis**.

### Обоснование

#### 1. Property-Based Testing - дополнение к unit-тестам
- **Не замена**: Hypothesis дополняет традиционные тесты
- **Для инвариантов**: Проверка свойств, которые должны быть истинны всегда
- **Для крайних случаев**: Автоматический поиск граничных условий
- **Для алгоритмов**: Проверка корректности сложной логики

#### 2. Hypothesis - стандарт де-факто
- **Зрелая библиотека**: Активно развивается с 2013 года
- **Широкое применение**: Используется в Django, pytest, NumPy
- **Отличная документация**: Понятные примеры и гайды
- **Интеграция с pytest**: Seamless integration

#### 3. Применение в проекте
**ContextManager** - критичный компонент с инвариантами:
- Контекст никогда не превышает `max_messages`
- При добавлении сообщений старые удаляются корректно
- Последовательность сообщений сохраняется
- Очистка контекста работает всегда

**MemoryStorage** - проверка корректности операций:
- Данные сохраняются и извлекаются корректно
- Очистка данных работает для любого user_id
- Состояние консистентно при любой последовательности операций

#### 4. Соответствие принципам проекта
- **Качество**: Высокая надежность критичных компонентов
- **KISS**: Меньше тестов, больше покрытие
- **Explicit**: Свойства системы документированы в тестах
- **Минимализм**: Одна дополнительная зависимость для значительного улучшения

## Последствия

### Положительные
- ✅ Автоматическое обнаружение крайних случаев
- ✅ Проверка инвариантов системы
- ✅ Высокое доверие к критичным компонентам
- ✅ Документирование свойств системы в коде
- ✅ Автоматическое упрощение найденных багов
- ✅ Регрессионное тестирование найденных случаев
- ✅ Меньше кода тестов при большем покрытии

### Отрицательные
- ⚠️ Немного медленнее выполнение тестов
- ⚠️ Требует изменения мышления от примеров к свойствам
- ⚠️ Дополнительная зависимость в dev requirements

### Нейтральные
- 📝 Комбинация с традиционными тестами
- 📝 Применяется только для критичных компонентов
- 📝 Pytest markers для раздельного запуска

## Реализация

### Установка
```bash
uv add --dev hypothesis>=6.0.0
```

### Конфигурация в pyproject.toml
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.12.0",
    "hypothesis>=6.0.0",  # Property-based testing
]

[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "property: Property-based tests with Hypothesis"
]
```

### Пример: Property-based тест для ContextManager
```python
# tests/test_context_manager_property.py
from hypothesis import given, strategies as st
from src.context_manager import ContextManager

@given(
    messages=st.lists(
        st.fixed_dictionaries({
            "role": st.sampled_from(["user", "assistant"]),
            "content": st.text(min_size=1, max_size=1000)
        }),
        min_size=0,
        max_size=100
    ),
    max_messages=st.integers(min_value=1, max_value=50)
)
@pytest.mark.property
def test_context_never_exceeds_max_messages(messages, max_messages):
    """Инвариант: контекст никогда не превышает max_messages"""
    memory_storage = MemoryStorage()
    context_manager = ContextManager(memory_storage, max_messages=max_messages)
    user_id = "test_user"

    for msg in messages:
        context_manager.add_message(user_id, msg)

    context = context_manager.get_context(user_id)
    assert len(context) <= max_messages

@given(st.lists(st.text(), min_size=1, max_size=50))
@pytest.mark.property
def test_context_preserves_order(messages):
    """Инвариант: порядок сообщений сохраняется"""
    memory_storage = MemoryStorage()
    context_manager = ContextManager(memory_storage, max_messages=100)
    user_id = "test_user"

    for msg in messages:
        context_manager.add_message(user_id, {"role": "user", "content": msg})

    context = context_manager.get_context(user_id)
    retrieved_messages = [m["content"] for m in context]

    # Последние N сообщений должны быть в том же порядке
    assert retrieved_messages == messages[-len(retrieved_messages):]
```

### Makefile команды
```makefile
test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

test-property:
	pytest -v -m property

test-all: test
	pytest -v

test:
	pytest -v --cov=src --cov-report=term-missing
```

### Пример найденного бага
```python
# Hypothesis найдет такой случай автоматически:
Falsifying example: test_context_never_exceeds_max(
    messages=[
        {"role": "user", "content": ""},  # Пустой контент!
        {"role": "user", "content": "a"},
    ],
    max_messages=1
)
# Hypothesis автоматически упростил пример до минимального
```

## Примеры применения

### 1. ContextManager - проверка инвариантов
```python
@given(st.lists(st.text(), max_size=100))
def test_clear_context_always_works(messages):
    """После clear контекст всегда пуст"""
    cm = ContextManager(max_messages=10)
    for msg in messages:
        cm.add_message("user", {"role": "user", "content": msg})
    cm.clear_context("user")
    assert len(cm.get_context("user")) == 0
```

### 2. MemoryStorage - проверка изоляции данных
```python
@given(
    user_ids=st.lists(st.text(min_size=1), min_size=2, max_size=10, unique=True),
    data=st.lists(st.dictionaries(st.text(), st.text()))
)
def test_storage_isolates_user_data(user_ids, data):
    """Данные пользователей изолированы друг от друга"""
    storage = MemoryStorage()
    for user_id, user_data in zip(user_ids, data):
        storage.set_context(user_id, user_data)

    # Проверка изоляции
    for user_id in user_ids:
        other_users = [uid for uid in user_ids if uid != user_id]
        user_context = storage.get_context(user_id)
        for other_user in other_users:
            other_context = storage.get_context(other_user)
            # Контексты не должны пересекаться
            assert user_context is not other_context
```

### 3. Интеграционный тест с property-based подходом
```python
@given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=20))
@pytest.mark.integration
@pytest.mark.property
def test_full_message_flow_preserves_history(messages):
    """История диалога сохраняется корректно при любой последовательности"""
    handler = create_test_handler()
    user_id = "test_user"

    for msg in messages:
        await handler.handle_message(user_id, msg)

    context = handler._context_manager.get_context(user_id)
    assert len(context) > 0
    assert all("role" in m and "content" in m for m in context)
```

## Стратегия применения

### Когда использовать Property-Based Testing
✅ **Используйте для:**
- Проверки инвариантов системы
- Тестирования граничных условий
- Критичных алгоритмов и структур данных
- Валидации входных данных
- Проверки консистентности состояния

❌ **Не используйте для:**
- Простых геттеров/сеттеров
- Тривиальных функций
- Внешних API (используйте моки)
- Тестирования конкретного бизнес-сценария

### Комбинация подходов
```python
# 1. Традиционный тест для конкретного сценария
def test_context_manager_basic_flow():
    """Конкретный пример использования"""
    cm = ContextManager(max_messages=3)
    cm.add_message("user", {"role": "user", "content": "Hello"})
    assert len(cm.get_context("user")) == 1

# 2. Property-based тест для инварианта
@given(st.lists(st.text(), max_size=100))
def test_context_manager_invariant(messages):
    """Свойство: контекст всегда <= max_messages"""
    cm = ContextManager(max_messages=10)
    for msg in messages:
        cm.add_message("user", {"role": "user", "content": msg})
    assert len(cm.get_context("user")) <= 10
```

## Альтернативы, которые были рассмотрены
- **Только традиционные тесты** - отклонено, не покрывают крайние случаи
- **QuickCheck (Haskell)** - отклонено, не для Python
- **FsCheck (.NET)** - отклонено, не для Python
- **Быстрая проверка вручную** - отклонено, ненадежно и трудоемко

## Связанные решения
- ADR-001: Использование Dependency Injection (упрощает тестирование)
- ADR-004: Ruff + Mypy (комплексный контроль качества)
- Итерация #4 в `tasklists/tasklist_tech_dept-sp0.md` (план внедрения)

## Метрики успеха
- Property-based тесты для ContextManager и MemoryStorage
- Обнаружение хотя бы 1 нового бага через Hypothesis
- Coverage критичных компонентов >= 90%
- Время выполнения property-based тестов < 30 секунд
- Регрессионные тесты для всех найденных Hypothesis примеров

---
**Дата:** 2025-10-11
**Автор:** Команда разработки
**Статус:** Предлагается к принятию

