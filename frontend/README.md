# Frontend - Dashboard и Web-чат

Frontend приложение для мониторинга и анализа диалогов бота, построенное на Next.js 14 с TypeScript и shadcn/ui.

## Технологический стек

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **UI Library**: shadcn/ui (на базе Radix UI)
- **Styling**: Tailwind CSS
- **Package Manager**: pnpm

## Быстрый старт

### Установка зависимостей

```bash
# Из корня проекта
make frontend-install

# Или напрямую
cd frontend
pnpm install
```

### Настройка переменных окружения

Создайте файл `.env.local` на основе примера:

```bash
# Скопируйте пример
cp .env.local.example .env.local

# Отредактируйте при необходимости
# По умолчанию используется http://localhost:8000
```

Содержимое `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Запуск dev сервера

```bash
# Из корня проекта
make frontend-dev

# Или напрямую
cd frontend
pnpm dev
```

Приложение будет доступно на `http://localhost:3000`

## Команды разработки

### Основные команды

```bash
make frontend-install      # Установка зависимостей
make frontend-dev         # Запуск dev сервера
make frontend-build       # Production сборка
make frontend-start       # Запуск production сервера
```

### Проверка качества кода

```bash
make frontend-lint        # ESLint проверка
make frontend-type-check  # TypeScript проверка типов
make frontend-format      # Форматирование кода (Prettier)
make frontend-quality     # Полная проверка качества
```

## Структура проекта

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx           # Корневой layout
│   │   ├── page.tsx             # Главная страница
│   │   └── globals.css          # Глобальные стили
│   ├── components/
│   │   └── ui/                  # shadcn/ui базовые компоненты
│   │       ├── button.tsx
│   │       └── card.tsx
│   ├── lib/
│   │   ├── api.ts              # API клиент для backend
│   │   └── utils.ts            # Утилиты (cn helper)
│   └── types/
│       └── api.ts              # TypeScript типы для API
├── public/                      # Статические файлы
├── doc/
│   ├── frontend-vision.md      # Техническое видение
│   └── frontend-roadmap.md     # Roadmap frontend
├── .env.local                  # Локальные переменные (не в git)
├── .env.local.example          # Пример конфигурации
├── next.config.ts              # Конфигурация Next.js
├── tsconfig.json               # Конфигурация TypeScript
├── tailwind.config.ts          # Конфигурация Tailwind CSS
├── components.json             # Конфигурация shadcn/ui
├── package.json                # Зависимости проекта
└── README.md                   # Этот файл
```

## API Интеграция

Frontend подключается к FastAPI backend через REST API.

### Endpoints

- `GET /health` - проверка работоспособности API
- `GET /api/stats?period={day|week}` - получение статистики

### Примеры использования

```typescript
import { checkApiHealth, getStats } from "@/lib/api";

// Проверка здоровья API
const health = await checkApiHealth();
console.log(health.status); // "ok"

// Получение статистики за день
const stats = await getStats("day");
console.log(stats.summary.total_conversations);
```

### Типы данных

Все типы синхронизированы с backend Pydantic моделями:

```typescript
interface StatsResponse {
  period: "day" | "week";
  summary: StatsSummary;
  activity_chart: ActivityPoint[];
  recent_conversations: RecentConversationItem[];
  top_users: TopUserItem[];
}
```

См. `src/types/api.ts` для полного списка типов.

## shadcn/ui компоненты

Проект использует shadcn/ui - коллекцию переиспользуемых компонентов на базе Radix UI.

### Установленные компоненты

- Button
- Card (+ CardHeader, CardTitle, CardDescription, CardContent)

### Добавление новых компонентов

```bash
cd frontend
pnpm dlx shadcn@latest add [component-name]
```

Примеры:
```bash
pnpm dlx shadcn@latest add dialog
pnpm dlx shadcn@latest add table
pnpm dlx shadcn@latest add chart
```

## TypeScript

Проект использует строгий режим TypeScript:

```json
{
  "strict": true,
  "noUncheckedIndexedAccess": true,
  "noImplicitAny": true,
  "strictNullChecks": true
}
```

### Path Aliases

Используйте `@/` для импортов:

```typescript
import { Button } from "@/components/ui/button";
import { getStats } from "@/lib/api";
import type { StatsResponse } from "@/types/api";
```

## Стилизация

### Tailwind CSS

Используется utility-first подход:

```tsx
<div className="flex items-center justify-center p-4 bg-primary text-primary-foreground">
  Content
</div>
```

### CSS Variables

Цвета определены через CSS переменные в `globals.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  /* ... */
}
```

### cn() Helper

Для объединения классов используйте `cn()`:

```typescript
import { cn } from "@/lib/utils";

<div className={cn("base-class", condition && "conditional-class", className)} />
```

## Разработка

### Линтинг и форматирование

Проект использует:
- **ESLint** - линтинг кода
- **Prettier** - форматирование кода
- **TypeScript** - проверка типов

Перед коммитом запустите:

```bash
make frontend-quality
```

### Соглашения по коду

- Используйте TypeScript strict mode
- Все типы явные (никаких `any`)
- Компоненты в PascalCase
- Функции и переменные в camelCase
- Используйте `@/` для импортов
- Сортируйте импорты автоматически (ESLint)

## API Documentation

Backend API документация доступна после запуска API сервера:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Roadmap

### Текущий статус: FE-SP-2 ✅

- ✅ Frontend Vision документ
- ✅ Инициализация Next.js проекта
- ✅ Настройка TypeScript и ESLint
- ✅ Установка shadcn/ui
- ✅ API клиент и типы
- ✅ Базовая страница-заглушка

### Следующие спринты

- **FE-SP-3**: Реализация Dashboard (визуализация статистики)
- **FE-SP-4**: Реализация ИИ-чата (text-to-SQL)
- **FE-SP-5**: Переход на Real API (интеграция с БД)

См. [frontend-roadmap.md](doc/frontend-roadmap.md) для деталей.

## Troubleshooting

### Backend API недоступен

Убедитесь, что backend API запущен:

```bash
# В другом терминале
make api-run
```

Проверьте `NEXT_PUBLIC_API_URL` в `.env.local`

### Ошибки TypeScript

Запустите проверку типов:

```bash
make frontend-type-check
```

### Ошибки линтера

Попробуйте автофикс:

```bash
cd frontend
pnpm lint --fix
```

## Ссылки

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

## Лицензия

Проект для внутреннего использования.

