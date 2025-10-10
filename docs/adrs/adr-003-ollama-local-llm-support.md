# ADR-003: Поддержка локального Ollama через OpenAI Client

## Статус
Принято

## Контекст
Проект использует OpenAI Client для работы с LLM через провайдер OpenRouter (см. ADR-002). Это решение обеспечивает:
- Унифицированный API для различных моделей
- Минимум зависимостей (только пакет `openai`)
- Гибкость в выборе моделей
- Экономическую эффективность

Однако для разработки и тестирования важно иметь возможность:
- Работать без затрат на API
- Иметь полный контроль над моделями
- Обеспечить офлайн-разработку
- Тестировать с локальными моделями

## Проблема
Необходимо обеспечить возможность использования локальных LLM (через Ollama) для:
- **Разработки** - без затрат на API во время разработки
- **Тестирования** - стабильное окружение для тестов
- **Демонстрации** - работа без интернета
- **Приватности** - данные не покидают локальную машину
- **Экспериментов** - быстрое переключение между моделями

При этом важно:
- Не добавлять новых зависимостей
- Сохранить простоту архитектуры (KISS)
- Обеспечить легкое переключение между провайдерами
- Использовать существующий код без изменений

## Решение архитектуры

### Использование OpenAI Client с Ollama через совместимый API
```python
# Никаких изменений в коде!
# Ollama предоставляет OpenAI-совместимый API

# Для OpenRouter:
openai_client = OpenAIClient(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4"
)

# Для Ollama (только изменение конфигурации):
openai_client = OpenAIClient(
    api_key="ollama",  # Любое значение
    base_url="http://localhost:11434/v1",
    model="llama2"
)
```

**Плюсы:**
- Нулевые изменения в коде
- Нулевые дополнительные зависимости
- Полная совместимость
- Максимальная простота (KISS)
- Легкое переключение через конфигурацию
- Соответствие принципу Open/Closed

**Минусы:**
- Зависимость от совместимости API Ollama с OpenAI
- Требуется установка и запуск Ollama отдельно

## Обоснование решения

### Архитектурное превосходство
Благодаря правильному архитектурному решению в ADR-002 (параметр `base_url`), OpenAI Client уже поддерживает любой OpenAI-совместимый провайдер:

```python
class OpenAIClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url  # ← Ключевой параметр для гибкости
        )
```

### Совместимость API
Ollama предоставляет полностью совместимый OpenAI API endpoint:
- **Chat Completions**: `/v1/chat/completions`
- **Формат запросов**: Идентичен OpenAI
- **Формат ответов**: Идентичен OpenAI
- **Потоковые ответы**: Поддерживаются

### Соответствие принципам проекта
- **KISS** - никаких изменений в коде
- **Минимум зависимостей** - ноль дополнительных пакетов
- **Explicit > Implicit** - явная конфигурация через `.env`
- **Open/Closed** - расширение без модификации

### Практические преимущества
- **Быстрое переключение** - изменение 2-3 переменных окружения
- **Разные профили** - `.env.openrouter` и `.env.ollama`
- **Локальная разработка** - без затрат на API
- **Приватность** - данные остаются локально

## Последствия

### Положительные
- ✅ Поддержка локальных LLM без изменений кода
- ✅ Нулевые дополнительные зависимости
- ✅ Легкое переключение между провайдерами
- ✅ Экономия на разработке и тестировании
- ✅ Возможность офлайн-работы
- ✅ Полная приватность данных при локальном использовании
- ✅ Подтверждение правильности архитектурного решения ADR-002

### Отрицательные
- ⚠️ Требуется установка Ollama отдельно
- ⚠️ Зависимость от поддержки совместимого API в Ollama
- ⚠️ Различия в производительности моделей

### Нейтральные
- 📝 Необходимость документирования настройки Ollama
- 📝 Разные наборы доступных моделей
- 📝 Различия в именовании моделей

## Реализация

### Конфигурация для OpenRouter (production)
```bash
# .env или .env.openrouter
TELEGRAM_BOT_TOKEN=your_telegram_token

# OpenRouter configuration
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4

LOG_LEVEL=INFO
MAX_CONTEXT_MESSAGES=10
```

### Конфигурация для Ollama (development)
```bash
# .env.ollama или .env.local
TELEGRAM_BOT_TOKEN=your_telegram_token

# Ollama local configuration
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama2

LOG_LEVEL=DEBUG
MAX_CONTEXT_MESSAGES=10
```

### Запуск Ollama
```bash
# Запуск сервера Ollama
ollama serve

# Проверка доступности
curl http://localhost:11434/v1/models
```

### Переключение между провайдерами
```bash
# Для production (OpenRouter)
cp .env.openrouter .env
make run

# Для development (Ollama)
cp .env.ollama .env
make run

# Или через переменные окружения
OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_MODEL=llama2 make run
```

### Доступные модели Ollama
```bash
# Список установленных моделей
ollama list

# Популярные модели для разработки
ollama pull llama2           # Универсальная модель
ollama pull mistral          # Быстрая и качественная
ollama pull codellama        # Для кода
ollama pull neural-chat      # Для диалогов
ollama pull phi              # Маленькая и быстрая
```

### Пример Settings класса
```python
class Settings:
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    
    # OpenAI-compatible LLM (OpenRouter или Ollama)
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENAI_MODEL: str = "openai/gpt-4"
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/"
    
    # Контекст
    MAX_CONTEXT_MESSAGES: int = 10
```

### Логирование
```python
# Логи будут показывать используемый провайдер
logger.info(f"llm_init|base_url={base_url}|model={model}")

# Для OpenRouter:
# llm_init|base_url=https://openrouter.ai/api/v1|model=openai/gpt-4

# Для Ollama:
# llm_init|base_url=http://localhost:11434/v1|model=llama2
```

### Тестирование
```python
def test_openai_client_with_ollama():
    """Тест совместимости с Ollama"""
    client = OpenAIClient(
        api_key="test",
        base_url="http://localhost:11434/v1",
        model="llama2"
    )
    
    # Тот же интерфейс работает с Ollama
    messages = [{"role": "user", "content": "Hello"}]
    response = client.send_message(messages, "You are a helpful assistant")
    
    assert response is not None
    assert isinstance(response, str)
```

## Альтернативные локальные провайдеры

Помимо Ollama, существуют другие локальные провайдеры с OpenAI-совместимым API, которые работают без изменений кода:

### LocalAI
Альтернатива Ollama с OpenAI-совместимым API.
- Работает аналогично Ollama
- Просто замените URL в конфигурации
- Не требует изменений кода

### LM Studio
GUI приложение для запуска локальных моделей.
- Предоставляет OpenAI-совместимый API
- Удобно для пользователей, предпочитающих GUI
- Не требует изменений кода

## Сравнение провайдеров

| Параметр | OpenRouter | Ollama | LocalAI | LM Studio |
|----------|------------|--------|---------|-----------|
| **Тип** | Облачный | Локальный | Локальный | Локальный |
| **Стоимость** | Pay-per-use | Бесплатно | Бесплатно | Бесплатно |
| **Интернет** | Требуется | Нет | Нет | Нет |
| **Модели** | Все популярные | Open-source | Open-source | Open-source |
| **Производительность** | Высокая | Зависит от GPU | Зависит от GPU | Зависит от GPU |
| **Приватность** | Низкая | Высокая | Высокая | Высокая |
| **Настройка** | API ключ | Установка | Docker | GUI установка |
| **API** | OpenAI-compatible | OpenAI-compatible | OpenAI-compatible | OpenAI-compatible |
| **Код изменения** | Нет | Нет | Нет | Нет |

## Рекомендации по использованию

### Для production (OpenRouter)
```bash
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4
```
**Когда использовать:**
- Production окружение
- Нужны мощные модели (GPT-4, Claude-3)
- Стабильная производительность
- Не критична стоимость

### Для development (Ollama)
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=mistral
```
**Когда использовать:**
- Локальная разработка
- Тестирование функционала
- Экономия на API
- Офлайн-разработка
- Эксперименты с моделями

### Для тестирования (Mock)
```python
# В тестах продолжаем использовать mock-объекты
mock_client = Mock(spec=OpenAIClient)
```

## Связанные решения
- ADR-001: Использование Dependency Injection
- ADR-002: Использование OpenAI Client с OpenRouter
- ADR-004: Подход к обработке ошибок (планируется)

## Метрики успеха
- ✅ Переключение между провайдерами < 1 минута
- ✅ Нулевые изменения в коде
- ✅ Экономия на разработке > 90%
- ✅ Время отклика Ollama < 10 секунд для простых запросов

## Примечания

### Важные моменты при использовании Ollama
1. **Ollama должен быть запущен**: `ollama serve`
2. **Модель должна быть загружена**: `ollama pull <model>`
3. **Первый запрос медленный**: Модель загружается в память
4. **Формат названий моделей**: Без префикса провайдера (`llama2` вместо `meta-llama/llama-2`)

### Ограничения локальных моделей
- Качество ответов может быть ниже, чем у GPT-4
- Требуется мощное железо (желательно GPU)
- Первый запрос может быть медленным
- Модели занимают место на диске (2-20 GB)

### Преимущества для разработки
- Мгновенная обратная связь без ожидания API
- Неограниченное количество запросов
- Полный контроль над окружением
- Возможность экспериментировать с параметрами

---
**Дата:** 2025-01-15  
**Автор:** Команда разработки  
**Статус:** Принято

**Ключевой вывод:** Правильное архитектурное решение (параметризация `base_url` в ADR-002) обеспечило поддержку локальных LLM без единой строки нового кода. Это демонстрирует силу принципов Open/Closed и KISS.

