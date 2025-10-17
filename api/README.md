# Bot Statistics API

Mock API для получения статистики диалогов бота. Предоставляет тестовые данные для разработки frontend дашборда.

## Запуск

```bash
# Установить зависимости
make install

# Запустить API сервер
make api-run
```

Сервер запустится на `http://localhost:8000`

## Документация

После запуска сервера доступна автоматическая документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### GET /health

Проверка работоспособности API.

**Пример запроса:**

```bash
curl http://localhost:8000/health
```

**Ответ:**

```json
{
  "status": "ok"
}
```

### GET /api/stats

Получение статистики диалогов за указанный период.

**Query параметры:**
- `period` (required): `day` | `week` - период для статистики

#### Пример 1: Статистика за день

```bash
curl "http://localhost:8000/api/stats?period=day"
```

**PowerShell:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day" | ConvertTo-Json -Depth 10
```

**Python:**

```python
import requests

response = requests.get("http://localhost:8000/api/stats", params={"period": "day"})
data = response.json()
print(f"Total conversations: {data['summary']['total_conversations']}")
```

**JavaScript (fetch):**

```javascript
fetch('http://localhost:8000/api/stats?period=day')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Структура ответа:**

```json
{
  "period": "day",
  "summary": {
    "total_conversations": 52,
    "active_users": 25,
    "average_conversation_length": 12.5,
    "total_messages": 650
  },
  "activity_chart": [
    {
      "date": "2025-10-17",
      "hour": 0,
      "message_count": 15,
      "conversation_count": 3
    },
    ...24 точки по часам...
  ],
  "recent_conversations": [
    {
      "id": 101,
      "user_id": 1001,
      "username": "alice_wonder",
      "message_count": 24,
      "created_at": "2025-10-17T10:15:00",
      "updated_at": "2025-10-17T12:25:00"
    },
    ...10 записей...
  ],
  "top_users": [
    {
      "user_id": 1001,
      "username": "alice_wonder",
      "first_name": "Alice",
      "conversation_count": 8,
      "message_count": 95
    },
    ...5 записей...
  ]
}
```

#### Пример 2: Статистика за неделю

```bash
curl "http://localhost:8000/api/stats?period=week"
```

**Структура ответа:**

```json
{
  "period": "week",
  "summary": {
    "total_conversations": 312,
    "active_users": 95,
    "average_conversation_length": 14.8,
    "total_messages": 4618
  },
  "activity_chart": [
    {
      "date": "2025-10-11",
      "hour": null,
      "message_count": 580,
      "conversation_count": 38
    },
    ...7 точек по дням...
  ],
  "recent_conversations": [
    ...15 записей...
  ],
  "top_users": [
    ...10 записей...
  ]
}
```

## Тестирование

```bash
# Запустить тесты через Makefile
make api-test
```

## Структура данных

### StatsSummary

- `total_conversations` (int) - Общее количество диалогов
- `active_users` (int) - Количество активных пользователей
- `average_conversation_length` (float) - Средняя длина диалога в сообщениях
- `total_messages` (int) - Общее количество сообщений

### ActivityPoint

- `date` (string) - Дата в формате YYYY-MM-DD
- `hour` (int | null) - Час дня (0-23) для периода "day", null для "week"
- `message_count` (int) - Количество сообщений
- `conversation_count` (int) - Количество диалогов

### RecentConversationItem

- `id` (int) - ID диалога
- `user_id` (int) - ID пользователя
- `username` (string | null) - Имя пользователя
- `message_count` (int) - Количество сообщений в диалоге
- `created_at` (datetime) - Время создания диалога
- `updated_at` (datetime) - Время последнего обновления

### TopUserItem

- `user_id` (int) - ID пользователя
- `username` (string | null) - Имя пользователя
- `first_name` (string | null) - Имя пользователя
- `conversation_count` (int) - Количество диалогов
- `message_count` (int) - Общее количество сообщений

## Архитектура

Модуль построен на основе паттерна Strategy с абстрактным интерфейсом `StatCollector`:

- `StatCollector` (ABC) - абстрактный интерфейс для сборщиков статистики
- `MockStatCollector` - Mock реализация с жестко заданными тестовыми данными
- `RealStatCollector` ✅ (Реализовано в FE-SP-4) - реальная реализация работающая с БД

### Переключение между Mock и Real

Режим работы контролируется через переменную окружения `.env`:

```bash
# .env file
USE_MOCK_STAT_COLLECTOR=false  # false = использовать реальную БД, true = Mock данные
DATABASE_URL=sqlite+aiosqlite:///data/bot.db
```

- `USE_MOCK_STAT_COLLECTOR=true` - использует `MockStatCollector` с фиксированными тестовыми данными
- `USE_MOCK_STAT_COLLECTOR=false` (по умолчанию) - использует `RealStatCollector` с данными из SQLite базы

Переключение происходит автоматически при запуске API сервера без изменений кода.

## CORS

API настроен с открытыми CORS настройками для разработки. В production необходимо указать конкретные разрешенные origins.

