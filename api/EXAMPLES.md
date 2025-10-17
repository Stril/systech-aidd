# Примеры запросов к API

Этот файл содержит примеры запросов к Bot Statistics API для тестирования и разработки.

## Базовый URL

```
http://localhost:8000
```

## Примеры с curl

### Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**

```json
{
  "status": "ok"
}
```

### Статистика за день

```bash
curl "http://localhost:8000/api/stats?period=day" | jq
```

**Ожидаемый ответ:** 52 диалога, 25 активных пользователей, 24 точки на графике (по часам)

### Статистика за неделю

```bash
curl "http://localhost:8000/api/stats?period=week" | jq
```

**Ожидаемый ответ:** 312 диалогов, 95 активных пользователей, 7 точек на графике (по дням)

### Ошибка: неверный период

```bash
curl "http://localhost:8000/api/stats?period=month"
```

**Ожидаемый ответ:** HTTP 422 (Validation Error)

## Примеры с PowerShell

### Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

### Статистика за день (formatted JSON)

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day"
$response | ConvertTo-Json -Depth 10
```

### Получить только summary

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day"
$response.summary
```

**Вывод:**

```
total_conversations      : 52
active_users            : 25
average_conversation_length : 12.5
total_messages          : 650
```

### Получить количество точек на графике

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=week"
$response.activity_chart.Count
```

**Вывод:** `7`

## Примеры с Python

### Базовый запрос

```python
import requests

response = requests.get("http://localhost:8000/api/stats", params={"period": "day"})
data = response.json()

print(f"Период: {data['period']}")
print(f"Всего диалогов: {data['summary']['total_conversations']}")
print(f"Активных пользователей: {data['summary']['active_users']}")
```

### Построение графика активности

```python
import requests
import matplotlib.pyplot as plt

response = requests.get("http://localhost:8000/api/stats", params={"period": "day"})
data = response.json()

hours = [point['hour'] for point in data['activity_chart']]
messages = [point['message_count'] for point in data['activity_chart']]

plt.figure(figsize=(12, 6))
plt.plot(hours, messages, marker='o')
plt.xlabel('Hour of Day')
plt.ylabel('Message Count')
plt.title('Message Activity by Hour')
plt.grid(True)
plt.savefig('activity_chart.png')
plt.show()
```

### Получить топ-5 пользователей

```python
import requests

response = requests.get("http://localhost:8000/api/stats", params={"period": "week"})
data = response.json()

print("Top 5 Users:")
for user in data['top_users'][:5]:
    print(f"- {user['first_name']} (@{user['username']}): {user['message_count']} messages")
```

### Async запрос с aiohttp

```python
import asyncio
import aiohttp

async def get_stats(period: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://localhost:8000/api/stats",
            params={"period": period}
        ) as response:
            return await response.json()

async def main():
    day_stats = await get_stats("day")
    week_stats = await get_stats("week")

    print(f"Day: {day_stats['summary']['total_conversations']} conversations")
    print(f"Week: {week_stats['summary']['total_conversations']} conversations")

asyncio.run(main())
```

## Примеры с JavaScript/TypeScript

### Fetch API (Browser)

```javascript
// Получить статистику за день
fetch('http://localhost:8000/api/stats?period=day')
  .then(response => response.json())
  .then(data => {
    console.log('Total conversations:', data.summary.total_conversations);
    console.log('Active users:', data.summary.active_users);
  })
  .catch(error => console.error('Error:', error));
```

### Async/Await

```javascript
async function getStats(period) {
  try {
    const response = await fetch(`http://localhost:8000/api/stats?period=${period}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching stats:', error);
  }
}

// Использование
const dayStats = await getStats('day');
console.log('Activity points:', dayStats.activity_chart.length);
```

### Node.js (с node-fetch)

```javascript
import fetch from 'node-fetch';

async function fetchStats() {
  const response = await fetch('http://localhost:8000/api/stats?period=week');
  const data = await response.json();

  console.log(`Week Statistics:`);
  console.log(`  Conversations: ${data.summary.total_conversations}`);
  console.log(`  Active Users: ${data.summary.active_users}`);
  console.log(`  Avg Length: ${data.summary.average_conversation_length}`);
}

fetchStats();
```

### Axios

```javascript
import axios from 'axios';

axios.get('http://localhost:8000/api/stats', {
  params: { period: 'day' }
})
  .then(response => {
    const { summary, activity_chart } = response.data;
    console.log('Summary:', summary);
    console.log('Chart points:', activity_chart.length);
  })
  .catch(error => console.error('Error:', error));
```

## TypeScript типы

```typescript
interface StatsSummary {
  total_conversations: number;
  active_users: number;
  average_conversation_length: number;
  total_messages: number;
}

interface ActivityPoint {
  date: string;
  hour: number | null;
  message_count: number;
  conversation_count: number;
}

interface RecentConversationItem {
  id: number;
  user_id: number;
  username: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface TopUserItem {
  user_id: number;
  username: string | null;
  first_name: string | null;
  conversation_count: number;
  message_count: number;
}

interface StatsResponse {
  period: 'day' | 'week';
  summary: StatsSummary;
  activity_chart: ActivityPoint[];
  recent_conversations: RecentConversationItem[];
  top_users: TopUserItem[];
}

// Использование
async function getStats(period: 'day' | 'week'): Promise<StatsResponse> {
  const response = await fetch(`http://localhost:8000/api/stats?period=${period}`);
  return response.json();
}
```

## Тестирование в Postman

### Создание коллекции

1. Создайте новую коллекцию "Bot Statistics API"
2. Добавьте переменную окружения `baseUrl` = `http://localhost:8000`

### Requests

#### Health Check

- **Method**: GET
- **URL**: `{{baseUrl}}/health`
- **Tests**:

```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Status is ok", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("ok");
});
```

#### Get Day Stats

- **Method**: GET
- **URL**: `{{baseUrl}}/api/stats`
- **Params**: `period` = `day`
- **Tests**:

```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has correct structure", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('period');
    pm.expect(jsonData).to.have.property('summary');
    pm.expect(jsonData).to.have.property('activity_chart');
    pm.expect(jsonData.period).to.eql('day');
});

pm.test("Activity chart has 24 points", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.activity_chart).to.have.lengthOf(24);
});
```

## WebSocket (для будущих real-time updates)

Примечание: Текущая версия API не поддерживает WebSocket, но это может быть добавлено в будущем.

```javascript
// Пример для будущей реализации
const ws = new WebSocket('ws://localhost:8000/ws/stats');

ws.onmessage = (event) => {
  const stats = JSON.parse(event.data);
  console.log('Real-time stats update:', stats);
};
```

