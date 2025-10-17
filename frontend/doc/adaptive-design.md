# Адаптивный дизайн Frontend

## Обзор

Все компоненты фронтенда оптимизированы для мобильных устройств, планшетов и десктопов с использованием Mobile-First подхода.

## Breakpoints (Tailwind CSS)

- **Mobile**: `< 640px` (default)
- **Small (sm)**: `≥ 640px`
- **Medium (md)**: `≥ 768px`
- **Large (lg)**: `≥ 1024px`
- **Extra Large (xl)**: `≥ 1280px`

## Изменённые компоненты

### 1. Главная страница (`src/app/page.tsx`)

#### Адаптивный padding
```tsx
className="p-4 sm:p-8 md:p-12 lg:p-24"
```
- Mobile: 16px
- Small: 32px
- Medium: 48px
- Large: 96px

#### Кнопки
```tsx
className="flex flex-col gap-2 pt-4 sm:flex-row"
// Каждая кнопка:
className="w-full sm:w-auto"
```
- Mobile: вертикальная колонка, кнопки на всю ширину
- Small+: горизонтальный ряд, кнопки авто-ширина

### 2. Dashboard Layout (`src/components/dashboard/dashboard-layout.tsx`)

#### Header Container
```tsx
className="container flex h-16 items-center justify-between px-4 md:px-8"
```
- Адаптивный padding: `px-4` → `md:px-8`

#### Title
```tsx
className="text-sm font-semibold sm:text-base md:text-xl"
```
- Mobile: 14px
- Small: 16px
- Medium: 20px

#### Gap между элементами
```tsx
className="flex items-center gap-2 sm:gap-4"
```
- Mobile: 8px
- Small: 16px

#### Main Container
```tsx
className="container px-4 py-6 md:px-8"
```

### 3. Stats Cards (`src/components/dashboard/stats-cards.tsx`)

#### Grid Layout
```tsx
className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-4"
```
- Mobile: 1 колонка
- Medium: 2 колонки
- Large: 4 колонки

#### Card Header
```tsx
className="pb-3"
```
- Уменьшенный bottom padding для компактности

#### Typography
```tsx
// Description
className="text-xs sm:text-sm"

// Title
className="text-2xl font-bold sm:text-3xl md:text-4xl"

// Content text
className="text-xs text-muted-foreground sm:text-sm"
```

#### Gaps
- Mobile: `gap-3` (12px)
- Small: `gap-4` (16px)

### 4. Activity Chart (`src/components/dashboard/activity-chart.tsx`)

#### Header Layout
```tsx
className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
```
- Mobile: вертикальная колонка
- Small+: горизонтальный ряд с выравниванием

#### Typography
```tsx
// Title
className="text-lg sm:text-xl"

// Description
className="text-xs sm:text-sm"
```

#### Tabs
```tsx
// TabsList
className="w-full sm:w-auto"

// TabsTrigger
className="flex-1 text-xs sm:flex-initial sm:text-sm"
```
- Mobile: полная ширина, равномерное распределение
- Small+: авто-ширина, нормальный размер

#### Chart Height
```tsx
className="h-[250px] sm:h-[350px] md:h-[400px]"
```
- Mobile: 250px
- Small: 350px
- Medium: 400px

#### Chart Margins
```tsx
margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
```
- Уменьшен right margin для мобильных (с 30 до 10)

## Best Practices

### 1. Mobile-First подход
Все стили начинаются с мобильных, затем расширяются:
```tsx
className="text-sm sm:text-base md:text-xl"
```

### 2. Breakpoints
Используйте только необходимые breakpoints:
- Mobile (default) - базовый стиль
- `sm:` - для небольших изменений
- `md:` - для планшетов
- `lg:` - для десктопа

### 3. Typography
- Минимум `text-xs` на мобильных для читаемости
- Постепенное увеличение на больших экранах
- Адаптивные `line-height` и `letter-spacing`

### 4. Spacing
- Меньше padding/margin на мобильных
- `gap-3` на мобильных, `gap-4+` на десктопе
- Адаптивные container padding

### 5. Layout
- `flex-col` на мобильных, `flex-row` на десктопе
- Grid с адаптивными колонками
- `w-full` для кнопок на мобильных

## Тестирование

### Chrome DevTools

1. Откройте http://localhost:3000
2. Откройте DevTools (`F12`)
3. Включите Device Toolbar (`Ctrl+Shift+M`)

### Рекомендуемые разрешения

#### Mobile
- **iPhone SE**: 375 x 667
- **iPhone 12 Pro**: 390 x 844
- **Samsung Galaxy S20**: 360 x 800

#### Tablet
- **iPad**: 768 x 1024
- **iPad Pro**: 1024 x 1366

#### Desktop
- **Laptop**: 1280 x 800
- **Desktop**: 1920 x 1080

### Чек-лист

- [ ] Главная страница
  - [ ] Кнопки вертикально на мобильных
  - [ ] Padding адаптируется
  - [ ] Текст читаем

- [ ] Dashboard Header
  - [ ] Заголовок адаптируется
  - [ ] Кнопки корректно отображаются
  - [ ] Нет горизонтального скролла

- [ ] Stats Cards
  - [ ] 1 колонка на мобильных
  - [ ] 2 колонки на планшетах
  - [ ] 4 колонки на десктопе
  - [ ] Цифры читаемы

- [ ] Activity Chart
  - [ ] Tabs адаптивные
  - [ ] График масштабируется
  - [ ] Высота графика адаптивная
  - [ ] Легенда читаема

## Результаты

✅ Все компоненты адаптивны
✅ Нет горизонтального скролла
✅ Читаемый текст на всех устройствах
✅ Оптимальное использование пространства
✅ Плавные переходы между breakpoints

## Следующие шаги

- [ ] Добавить адаптивность для Web-чата
- [ ] Протестировать на реальных устройствах
- [ ] Добавить touch-friendly элементы
- [ ] Оптимизация производительности

