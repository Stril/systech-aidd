# Dashboard Components Documentation

Документация компонентов Dashboard для визуализации статистики диалогов бота.

## Структура компонентов

```
/dashboard (route)
  └── DashboardLayout
      └── DashboardPage (Client Component)
          ├── StatsCards
          └── ActivityChart
```

## Компоненты

### DashboardLayout

**Файл**: `src/components/dashboard/dashboard-layout.tsx`

**Описание**: Основной layout для dashboard с header, содержащим навигацию и элементы управления.

**Props**:
```typescript
interface DashboardLayoutProps {
  children: React.ReactNode;
}
```

**Особенности**:
- Sticky header с backdrop blur эффектом
- GitHub ссылка (левый верхний угол)
- Заголовок "Bot Statistics Dashboard"
- ThemeToggle кнопка (правый верхний угол)
- Responsive container для контента

**Использование**:
```tsx
<DashboardLayout>
  <DashboardPage initialStats={stats} />
</DashboardLayout>
```

---

### DashboardPage

**Файл**: `src/components/dashboard/dashboard-page.tsx`

**Описание**: Главный Client Component dashboard с state management и интеграцией API.

**Props**:
```typescript
interface DashboardPageProps {
  initialStats: StatsResponse;
}
```

**State**:
- `period: Period` - текущий выбранный период ("day" | "week")
- `stats: StatsResponse` - данные статистики из API
- `isLoading: boolean` - индикатор загрузки
- `error: string | null` - сообщение об ошибке

**Особенности**:
- Управление сменой периода
- Автоматическая загрузка данных при смене периода
- Обработка ошибок с UI feedback
- Передача данных в дочерние компоненты

**Использование**:
```tsx
// В Server Component
const initialStats = await getStats("day");

<DashboardPage initialStats={initialStats} />
```

---

### StatsCards

**Файл**: `src/components/dashboard/stats-cards.tsx`

**Описание**: Grid из 4 карточек с ключевыми метриками.

**Props**:
```typescript
interface StatsCardsProps {
  summary: StatsSummary;
}

interface StatsSummary {
  total_conversations: number;
  active_users: number;
  average_conversation_length: number;
  total_messages: number;
}
```

**Отображаемые метрики**:
1. **Total Conversations** - общее количество диалогов
2. **Active Users** - количество активных пользователей
3. **Avg. Conversation Length** - средняя длина диалога (с 1 знаком после запятой)
4. **Total Messages** - общее количество сообщений

**Форматирование**:
- Целые числа: форматируются с разделителями тысяч (`1,234`)
- Average length: отображается с 1 знаком после запятой (`14.8`)

**Responsive**:
- Desktop (lg+): 4 колонки
- Tablet (md): 2 колонки
- Mobile (sm): 1 колонка

**Использование**:
```tsx
<StatsCards summary={stats.summary} />
```

---

### ActivityChart

**Файл**: `src/components/dashboard/activity-chart.tsx`

**Описание**: Area график активности пользователей с переключателем периодов.

**Props**:
```typescript
interface ActivityChartProps {
  activityData: ActivityPoint[];
  period: Period;
  onPeriodChange: (period: Period) => void;
  isLoading?: boolean;
}

interface ActivityPoint {
  date: string;           // YYYY-MM-DD
  hour: number | null;    // 0-23 для day, null для week
  message_count: number;
  conversation_count: number;
}

type Period = "day" | "week";
```

**Особенности**:
- Две линии графика: Messages (синяя) и Conversations (зеленая)
- Gradient fill под линиями
- Tabs переключатель периодов:
  - "Last 24 hours" - данные по часам (0-23)
  - "Last 7 days" - данные по дням недели
- Tooltip с деталями при hover
- Legend с названиями линий
- Loading состояние с индикатором
- Плавная анимация при загрузке данных

**Ось X**:
- Day период: часы в формате "HH:00" (00:00, 01:00, ...)
- Week период: даты в формате "MMM DD" (Oct 17, Oct 18, ...)

**Использование**:
```tsx
<ActivityChart
  activityData={stats.activity_chart}
  period={period}
  onPeriodChange={handlePeriodChange}
  isLoading={isLoading}
/>
```

---

### ThemeToggle

**Файл**: `src/components/theme-toggle.tsx`

**Описание**: Кнопка переключения между темной и светлой темой.

**Props**: Нет props

**Особенности**:
- Использует `next-themes` для управления темой
- Иконки:
  - Sun icon - показывается в dark теме (переключение на light)
  - Moon icon - показывается в light теме (переключение на dark)
- Плавная анимация иконок (rotate on hover)
- Сохранение выбора в localStorage
- Hydration-safe (избегает mismatch между server и client)

**Использование**:
```tsx
<ThemeToggle />
```

---

### ThemeProvider

**Файл**: `src/components/theme-provider.tsx`

**Описание**: Provider для управления темами через `next-themes`.

**Props**:
```typescript
interface ThemeProviderProps {
  children: ReactNode;
}
```

**Конфигурация**:
- `attribute="class"` - переключение через класс `.dark`
- `defaultTheme="dark"` - темная тема по умолчанию
- `enableSystem={false}` - не использовать system preference
- `disableTransitionOnChange={false}` - плавные переходы

**Использование**:
```tsx
// В root layout
<html lang="ru" suppressHydrationWarning>
  <body>
    <ThemeProvider>
      {children}
    </ThemeProvider>
  </body>
</html>
```

---

## Утилиты

### Formatters

**Файл**: `src/lib/formatters.ts`

Утилиты для форматирования данных.

**Функции**:

```typescript
// Форматирование чисел с разделителями тысяч
formatNumber(value: number): string
// Пример: formatNumber(1234) => "1,234"

// Форматирование даты
formatDate(date: string): string
// Пример: formatDate("2025-10-17") => "17 Oct 2025"

// Форматирование даты и времени
formatDateTime(date: string): string
// Пример: formatDateTime("2025-10-17T10:15:00") => "17 Oct 2025, 10:15"

// Форматирование процентов
formatPercentage(value: number): string
// Пример: formatPercentage(12.5) => "12.5%"

// Получение инициалов из имени
getInitials(name: string): string
// Пример: getInitials("Alice Wonder") => "AW"

// Форматирование часа для графика
formatHour(hour: number): string
// Пример: formatHour(9) => "09:00"

// Короткое форматирование даты для графика
formatShortDate(date: string): string
// Пример: formatShortDate("2025-10-17") => "Oct 17"
```

---

## API Integration

### getStats

**Файл**: `src/lib/api.ts`

```typescript
async function getStats(period: Period): Promise<StatsResponse>
```

**Описание**: Загружает статистику для указанного периода.

**Параметры**:
- `period: "day" | "week"` - период для статистики

**Возвращает**: `StatsResponse` с полными данными статистики

**Ошибки**: Throws `ApiError` при ошибках API или сети

**Использование**:
```typescript
try {
  const stats = await getStats("day");
  console.log(stats.summary.total_conversations);
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error: ${error.status} - ${error.message}`);
  }
}
```

---

## Типы

### API Types

**Файл**: `src/types/api.ts`

Все TypeScript интерфейсы синхронизированы с backend Pydantic моделями.

**Основные типы**:
- `Period` - "day" | "week"
- `StatsResponse` - полный ответ API
- `StatsSummary` - сводная статистика
- `ActivityPoint` - точка данных для графика
- `RecentConversationItem` - информация о диалоге
- `TopUserItem` - информация о топ пользователе

---

## Примеры использования

### Полный flow Dashboard

```typescript
// pages/dashboard/page.tsx (Server Component)
import { getStats } from "@/lib/api";
import { DashboardLayout } from "@/components/dashboard/dashboard-layout";
import { DashboardPage } from "@/components/dashboard/dashboard-page";

export default async function Dashboard() {
  const initialStats = await getStats("day");

  return (
    <DashboardLayout>
      <DashboardPage initialStats={initialStats} />
    </DashboardLayout>
  );
}
```

### Обработка ошибок

```typescript
// В DashboardPage при смене периода
const handlePeriodChange = async (newPeriod: Period) => {
  setPeriod(newPeriod);
  setIsLoading(true);
  setError(null);

  try {
    const newStats = await getStats(newPeriod);
    setStats(newStats);
  } catch (err) {
    setError(err instanceof Error ? err.message : "Failed to load stats");
  } finally {
    setIsLoading(false);
  }
};
```

---

## Стилизация

### Темы

Dashboard поддерживает две темы:
- **Dark** (по умолчанию) - темная цветовая схема
- **Light** - светлая цветовая схема

Темы управляются через CSS переменные в `globals.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  /* ... */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```

### Tailwind Classes

Основные утилиты:
- `bg-background` / `text-foreground` - основные цвета
- `bg-card` / `text-card-foreground` - цвета карточек
- `text-muted-foreground` - приглушенный текст
- `border` / `shadow` - границы и тени

---

## Тестирование

### Unit Tests

**Форматтеры**:
```bash
pnpm test src/__tests__/lib/formatters.test.ts
```

**Компоненты**:
```bash
pnpm test src/__tests__/components/
```

### Coverage

Запуск с coverage отчетом:
```bash
pnpm test:coverage
```

Текущее покрытие: **70%+**

---

## Troubleshooting

### API недоступен

Если dashboard показывает ошибку подключения:
1. Проверьте что API сервер запущен: `make api-run`
2. Проверьте `NEXT_PUBLIC_API_URL` в `.env.local`
3. Откройте http://localhost:8000/docs для проверки API

### Темы не переключаются

1. Проверьте что `ThemeProvider` обернут в root layout
2. Проверьте `suppressHydrationWarning` в `<html>` теге
3. Очистите localStorage: `localStorage.removeItem('theme')`

### Данные не обновляются

1. Проверьте Network tab в DevTools
2. Убедитесь что `onPeriodChange` вызывается
3. Проверьте console на ошибки API

---

## Дальнейшее развитие

### Запланированные улучшения

- [ ] Добавление Real-time updates (WebSocket)
- [ ] Экспорт данных в CSV/PDF
- [ ] Фильтрация по пользователям
- [ ] Drill-down в конкретные диалоги
- [ ] Dark mode toggle в UI (уже реализовано)
- [ ] Расширенная аналитика

### Известные ограничения

- Desktop only (минимальная ширина 1024px)
- Данные обновляются только при ручной смене периода
- Нет кэширования данных
- Mock API используется (замена на Real в FE-SP-5)

---

## Ссылки

- [Frontend Vision](./frontend-vision.md)
- [Dashboard Requirements](./dashboard-requirements.md)
- [Frontend Roadmap](./frontend-roadmap.md)
- [API Documentation](../../api/README.md)

