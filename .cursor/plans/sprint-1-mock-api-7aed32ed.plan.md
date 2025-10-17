<!-- 7aed32ed-a360-4b73-8c53-5a9b3b1d0046 f54a1c5a-f818-4964-8c70-cd78e07c3aea -->
# Sprint 1: Mock API для дашборда статистики

## Обзор

Создание независимого API модуля с Mock реализацией сборщика статистики для разработки frontend дашборда. API будет предоставлять тестовые данные через REST endpoint с автоматической OpenAPI документацией.

## Структура файлов

Новая папка `api/` в корне проекта:

```
api/
├── __init__.py
├── main.py              # FastAPI entrypoint
├── models.py            # Pydantic модели для API контракта
├── stat_collector.py    # Абстрактный интерфейс StatCollector
└── mock_stat_collector.py  # Mock реализация с тестовыми данными
```

## API Контракт

### Endpoint: GET /api/stats

**Query параметр:**

- `period`: `day` | `week` (required)

**Response структура:**

```json
{
  "period": "day",
  "summary": {
    "total_conversations": 156,
    "active_users": 45,
    "average_conversation_length": 12.5,
    "total_messages": 1248
  },
  "activity_chart": [
    {"date": "2025-10-17", "hour": 0, "message_count": 45, "conversation_count": 8},
    {"date": "2025-10-17", "hour": 1, "message_count": 38, "conversation_count": 6},
    ...
  ],
  "recent_conversations": [
    {
      "id": 123,
      "user_id": 456,
      "username": "john_doe",
      "message_count": 15,
      "created_at": "2025-10-17T10:30:00Z",
      "updated_at": "2025-10-17T11:45:00Z"
    },
    ...
  ],
  "top_users": [
    {
      "user_id": 789,
      "username": "active_user",
      "first_name": "John",
      "conversation_count": 25,
      "message_count": 380
    },
    ...
  ]
}
```

## Детальная реализация

### 1. Pydantic модели (api/models.py)

Создать dataclasses для типизированного контракта:

- `StatsRequest` - валидация query параметра period
- `StatsSummary` - общая статистика
- `ActivityPoint` - точка на графике активности
- `RecentConversationItem` - информация о диалоге
- `TopUserItem` - статистика пользователя
- `StatsResponse` - полный ответ API

### 2. Абстрактный интерфейс (api/stat_collector.py)

```python
from abc import ABC, abstractmethod
from api.models import StatsResponse

class StatCollector(ABC):
    @abstractmethod
    async def get_stats(self, period: str) -> StatsResponse:
        """Collect statistics for specified period"""
        pass
```

### 3. Mock реализация (api/mock_stat_collector.py)

Класс `MockStatCollector` с методом `get_stats()`:

- Жестко заданные (hardcoded) данные на основе референса дашборда
- Фиксированные датасеты для day/week периодов
- Реалистичные значения метрик без случайной генерации
- Массивы фиксированной длины: day (24 точки по часам), week (7 точек по дням)
- Константные данные для упрощения отладки frontend

### 4. FastAPI приложение (api/main.py)

```python
from fastapi import FastAPI, Query
from api.stat_collector import StatCollector
from api.mock_stat_collector import MockStatCollector
from api.models import StatsResponse

app = FastAPI(
    title="Bot Statistics API",
    description="API для получения статистики диалогов бота",
    version="1.0.0"
)

collector: StatCollector = MockStatCollector()

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(
    period: str = Query(..., regex="^(day|week)$")
) -> StatsResponse:
    return await collector.get_stats(period)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

### 5. Зависимости

Добавить в `pyproject.toml`:

```toml
dependencies = [
    ...existing...,
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
]
```

### 6. Makefile команды

```makefile
# Запуск API сервера
api-run:
	uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Открыть API документацию
api-docs:
	@echo "Opening API docs at http://localhost:8000/docs"
	@python -m webbrowser http://localhost:8000/docs

# Тестовый запрос к API
api-test:
	curl "http://localhost:8000/api/stats?period=day" | python -m json.tool
```

### 7. Mock данные

Жестко заданные значения для периодов:

**Day:**

- total_conversations: 52
- active_users: 25
- average_conversation_length: 12.5
- total_messages: 650
- activity_chart: 24 точки (по часам с 00:00 до 23:00)
- recent_conversations: 10 записей
- top_users: 5 записей

**Week:**

- total_conversations: 312
- active_users: 95
- average_conversation_length: 14.8
- total_messages: 4618
- activity_chart: 7 точек (по дням недели)
- recent_conversations: 15 записей
- top_users: 10 записей

## Проверка результата

1. Установить зависимости: `make install`
2. Запустить API: `make api-run`
3. Открыть документацию: http://localhost:8000/docs
4. Протестировать endpoints через Swagger UI
5. Проверить команду: `make api-test`

## Ожидаемые результаты

- ✅ Работающий FastAPI сервер на порту 8000
- ✅ Автоматическая OpenAPI документация на /docs
- ✅ Endpoint GET /api/stats с валидацией period
- ✅ Реалистичные Mock данные для всех периодов
- ✅ Типизированный контракт через Pydantic
- ✅ Готовность к независимой разработке frontend

### To-dos

- [ ] Создать структуру папки api/ и базовые файлы
- [ ] Реализовать Pydantic модели для API контракта
- [ ] Создать абстрактный интерфейс StatCollector
- [ ] Реализовать MockStatCollector с генерацией тестовых данных
- [ ] Создать FastAPI приложение с endpoint /api/stats
- [ ] Добавить FastAPI и uvicorn в pyproject.toml
- [ ] Добавить команды api-run, api-docs, api-test в Makefile
- [ ] Протестировать API и проверить документацию