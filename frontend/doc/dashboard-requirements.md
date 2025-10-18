# Требования к Dashboard

## Общее описание

Dashboard - веб-интерфейс для визуализации статистики диалогов Telegram-бота с пользователями. Предоставляет администратору ключевые метрики и графики активности за выбранный период (день или неделя).

## Функциональные требования

### FR-1: Отображение ключевых метрик

Dashboard должен отображать 4 основные метрики в виде карточек:

1. **Total Conversations** - Общее количество диалогов за период
2. **Active Users** - Количество активных пользователей за период
3. **Average Conversation Length** - Средняя длина диалога в сообщениях
4. **Total Messages** - Общее количество сообщений за период

**Требования к отображению**:
- Крупное числовое значение
- Описательный текст под значением
- Grid layout - 4 карточки в ряд на desktop
- Темная карточка с контрастным текстом

### FR-2: График активности

График должен визуализировать активность пользователей за выбранный период:

**Данные на графике**:
- Две линии: количество сообщений (messages) и количество диалогов (conversations)
- Для периода "Day": 24 точки по часам (0-23)
- Для периода "Week": 7 точек по дням

**Интерактивность**:
- Tooltip при наведении на точку графика
- Легенда с названиями линий
- Плавная анимация при загрузке и смене данных

### FR-3: Переключение периода

Пользователь может выбрать период для отображения статистики:
- **Day** - статистика за последние 24 часа
- **Week** - статистика за последние 7 дней

**Требования**:
- Tabs компонент над или внутри графика
- Активный период визуально выделен
- При смене периода происходит загрузка новых данных из API
- Loading индикатор во время загрузки

### FR-4: Переключение темы

Dashboard поддерживает две темы оформления:
- **Dark** (по умолчанию) - темная тема
- **Light** - светлая тема

**Требования**:
- Кнопка переключения в header (правый верхний угол)
- Иконка Sun для светлой темы, Moon для темной
- Выбор темы сохраняется в localStorage
- Плавный переход между темами

### FR-5: Ссылка на GitHub

В header Dashboard должна быть кнопка-ссылка на GitHub репозиторий проекта:
- URL: `https://github.com/aidialogs/systech-aidd/tree/main`
- Расположение: левый верхний угол header
- Иконка GitHub
- Открывается в новой вкладке
- Tooltip "View on GitHub" при hover

## Технические требования

### TR-1: Интеграция с API

**Endpoint**: `GET /api/stats?period={day|week}`

**Backend URL**: `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_URL`)

**Response типы**: Синхронизированы с backend Pydantic моделями (см. `src/types/api.ts`)

**Обработка ошибок**:
- Отображение ошибки если API недоступен
- Retry механизм при временных сбоях
- Graceful fallback UI

### TR-2: Технологический стек

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **UI Components**: shadcn/ui на базе Radix UI
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Themes**: next-themes
- **Date formatting**: date-fns
- **Testing**: Vitest + React Testing Library

### TR-3: Целевая платформа

**Desktop only**:
- Минимальная ширина экрана: 1024px (lg breakpoint)
- Оптимальная ширина: 1280px+ (xl breakpoint)
- Нет адаптации для mobile и tablet
- Предупреждение для пользователей с узкими экранами (опционально)

### TR-4: TypeScript строгая типизация

- `strict: true` в tsconfig.json
- Все компоненты и функции полностью типизированы
- Никаких `any` типов
- Props интерфейсы для всех компонентов
- Type-safe API клиент

### TR-5: Качество кода

**ESLint**:
- `next/core-web-vitals` правила
- `@typescript-eslint/recommended` правила
- Нет ошибок перед коммитом

**Prettier**:
- Автоматическое форматирование
- Consistent code style

**Проверки**:
- `make frontend-lint` - без ошибок
- `make frontend-type-check` - без ошибок
- `make frontend-format` - код отформатирован

### TR-6: Тестирование

**Coverage**: >= 80%

**Типы тестов**:
1. **Unit тесты**:
   - Утилиты форматирования (formatters.ts)
   - Изолированные компоненты

2. **Component тесты**:
   - StatsCards - отображение метрик
   - ActivityChart - рендеринг графика
   - ThemeToggle - переключение тем

3. **Integration тесты**:
   - DashboardPage - полный flow
   - API интеграция с mock
   - Смена периода и обновление данных

**Команды**:
- `make frontend-test` - запуск тестов
- `make frontend-test-coverage` - с отчетом coverage

## UI/UX требования

### UX-1: Референсный дизайн

**Файл**: `frontend/doc/reference-dashboard.png`

Dashboard должен следовать референсному дизайну:
- Темная цветовая схема
- Минималистичный современный интерфейс
- Четкая визуальная иерархия
- Достаточные отступы и spacing

### UX-2: Loading состояния

**Initial load**:
- Skeleton loaders для карточек
- Placeholder для графика
- Smooth transition к реальным данным

**Смена периода**:
- Loading indicator над/внутри графика
- Disabled состояние tabs во время загрузки
- Opacity transition для контента

### UX-3: Обработка ошибок

**API errors**:
- Понятное сообщение об ошибке
- Кнопка "Try again" для retry
- Информация о состоянии backend (если доступна)

**Network errors**:
- "Unable to connect to API" сообщение
- Проверка NEXT_PUBLIC_API_URL конфигурации
- Ссылка на troubleshooting документацию

### UX-4: Анимации и переходы

**Плавные transitions**:
- Смена данных на графике (300ms ease)
- Переключение темы (200ms)
- Hover эффекты на карточках
- Loading спиннеры и скелетоны

**Без резких изменений**:
- Graceful data updates
- Smooth color transitions
- Progressive loading

### UX-5: Accessibility (базовая)

- Семантичная HTML разметка
- Alt тексты для изображений
- Keyboard navigation для интерактивных элементов
- Контрастные цвета (соответствие WCAG AA)
- Focus indicators для кнопок и ссылок

## Структура компонентов

```
/dashboard
  ├── page.tsx (Server Component)
  │   └── DashboardPage (Client Component)
  │       ├── Header
  │       │   ├── GitHubLink
  │       │   ├── Title
  │       │   └── ThemeToggle
  │       ├── StatsCards
  │       │   └── StatCard × 4
  │       └── ActivityChart
  │           ├── TabsSelector (Day/Week)
  │           └── AreaChart (Recharts)
```

## API контракт

### Request

```
GET /api/stats?period=day
GET /api/stats?period=week
```

### Response

```typescript
interface StatsResponse {
  period: "day" | "week";
  summary: {
    total_conversations: number;
    active_users: number;
    average_conversation_length: number;
    total_messages: number;
  };
  activity_chart: Array<{
    date: string;           // "YYYY-MM-DD"
    hour: number | null;    // 0-23 for day, null for week
    message_count: number;
    conversation_count: number;
  }>;
  recent_conversations: Array<...>;  // Не используется в UI
  top_users: Array<...>;            // Не используется в UI
}
```

## Файловая структура

```
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx              # Dashboard route
│   │   ├── layout.tsx                # Root layout с ThemeProvider
│   │   ├── page.tsx                  # Home page с ссылкой на dashboard
│   │   └── globals.css               # Global styles + theme variables
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── dashboard-page.tsx    # Main dashboard component
│   │   │   ├── stats-cards.tsx       # Metrics cards
│   │   │   ├── activity-chart.tsx    # Activity graph
│   │   │   └── dashboard-layout.tsx  # Header + layout
│   │   ├── theme-provider.tsx        # next-themes provider
│   │   ├── theme-toggle.tsx          # Theme switch button
│   │   └── ui/                       # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── tabs.tsx
│   │       └── [chart components]
│   ├── lib/
│   │   ├── api.ts                    # API client
│   │   ├── formatters.ts             # Formatting utilities
│   │   └── utils.ts                  # General utilities
│   └── types/
│       └── api.ts                    # TypeScript API types
├── doc/
│   ├── dashboard-requirements.md     # This document
│   ├── dashboard-components.md       # Components documentation
│   ├── frontend-vision.md            # Technical vision
│   └── frontend-roadmap.md           # Development roadmap
└── vitest.config.ts                  # Vitest configuration
```

## Definition of Done

- [ ] Dashboard доступен по URL `/dashboard`
- [ ] Все 4 метрики отображаются корректно из API
- [ ] График активности работает с данными за day/week
- [ ] Переключение периода загружает новые данные
- [ ] Переключатель темы работает и сохраняется
- [ ] GitHub ссылка открывается в новой вкладке
- [ ] Loading состояния реализованы
- [ ] Ошибки API обрабатываются gracefully
- [ ] TypeScript проверка проходит без ошибок
- [ ] ESLint проверка проходит без ошибок
- [ ] Тесты написаны (coverage >= 80%)
- [ ] Все тесты проходят успешно
- [ ] Документация обновлена
- [ ] Код отформатирован (Prettier)
- [ ] `make frontend-quality` выполняется без ошибок

## Приоритеты

**P0 (Must have)**:
- Метрики cards
- График активности
- Переключение периода
- API интеграция
- Темная тема

**P1 (Should have)**:
- Переключатель темы (light/dark)
- GitHub ссылка
- Loading состояния
- Error handling

**P2 (Nice to have)**:
- Анимации и transitions
- Accessibility улучшения
- Расширенная обработка ошибок

## Ссылки

- [Frontend Vision](./frontend-vision.md)
- [Frontend Roadmap](./frontend-roadmap.md)
- [API Documentation](../../api/README.md)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [Next.js Docs](https://nextjs.org/docs)
- [Recharts Docs](https://recharts.org)

