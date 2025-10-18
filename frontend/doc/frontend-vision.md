# Техническое видение Frontend проекта

## 1. Технологии

### Обязательные технологии:
- **Next.js 14+** - React фреймворк с App Router
- **TypeScript** - типизированный JavaScript
- **Tailwind CSS** - utility-first CSS framework
- **shadcn/ui** - React компоненты на базе Radix UI
- **pnpm** - быстрый пакетный менеджер

### Дополнительные технологии:
- **ESLint** - линтер для JavaScript/TypeScript
- **Prettier** - форматтер кода
- **Vitest** - unit-тестирование (будет добавлено в FE-SP-3)
- **React Testing Library** - тестирование компонентов (будет добавлено в FE-SP-3)
- **Zod** - валидация данных и схем

### Принципы выбора:
- Максимальная простота и производительность
- Современный стек с TypeScript strict mode
- Компонентный подход (shadcn/ui)
- Server Components и Client Components (Next.js App Router)
- Интеграция с существующим FastAPI backend

## 2. Принципы разработки

### Основные принципы:
- **KISS (Keep It Simple, Stupid)** - максимальная простота во всем
- **Компонентный подход** - переиспользуемые UI компоненты
- **Типобезопасность** - строгая типизация TypeScript
- **Responsive First** - адаптивный дизайн с mobile-first подходом

### Принципы кодирования:
- **Single Responsibility** - каждый компонент отвечает за одну задачу
- **Composition over Inheritance** - композиция вместо наследования
- **Type Safety** - строгая типизация всех данных и API
- **Explicit is better than implicit** - явность лучше неявности

### Структурные принципы:
- Понятная структура директорий
- Разделение Server и Client компонентов
- API клиент с типизацией
- Централизованная обработка ошибок

## 3. Структура проекта

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx           # Корневой layout
│   │   ├── page.tsx             # Главная страница
│   │   ├── globals.css          # Глобальные стили
│   │   └── dashboard/           # Dashboard страница (FE-SP-3)
│   ├── components/
│   │   ├── ui/                  # shadcn/ui базовые компоненты
│   │   ├── dashboard/           # Dashboard компоненты (FE-SP-3)
│   │   └── chat/                # Chat компоненты (FE-SP-4)
│   ├── lib/
│   │   ├── api.ts              # API клиент для backend
│   │   ├── utils.ts            # Утилиты (cn, formatters)
│   │   └── constants.ts        # Константы приложения
│   └── types/
│       └── api.ts              # TypeScript типы для API
├── public/                      # Статические файлы
├── doc/
│   ├── frontend-vision.md      # Этот документ
│   └── frontend-roadmap.md     # Roadmap frontend
├── .env.local                  # Локальные переменные окружения (не в git)
├── .env.local.example          # Пример конфигурации
├── next.config.ts              # Конфигурация Next.js
├── tsconfig.json               # Конфигурация TypeScript
├── tailwind.config.ts          # Конфигурация Tailwind CSS
├── components.json             # Конфигурация shadcn/ui
├── package.json                # Зависимости проекта
├── pnpm-lock.yaml             # Lock файл для pnpm
└── README.md                   # Документация проекта
```

### Принципы структуры:
- **src/app/** - страницы и layouts по Next.js App Router
- **src/components/** - переиспользуемые React компоненты
- **src/lib/** - утилиты, API клиенты, хелперы
- **src/types/** - TypeScript типы и интерфейсы
- **Компоненты по функциям** - dashboard/, chat/, ui/
- **Плоская структура** - минимум вложенности

## 4. Архитектура приложения

### Компоненты системы:

1. **Next.js App Router** - роутинг и серверные компоненты
2. **API Client** - типизированный клиент для backend API
3. **UI Components** - переиспользуемые компоненты из shadcn/ui
4. **Dashboard** - визуализация статистики диалогов (FE-SP-3)
5. **AI Chat** - web-интерфейс для администратора (FE-SP-4)

### Паттерны:

#### Server Components vs Client Components
- Server Components по умолчанию для статического контента
- Client Components (use client) для интерактивности
- Данные загружаются на сервере где возможно

#### API Integration
- Типизированный API клиент с обработкой ошибок
- Маппинг Python Pydantic моделей → TypeScript интерфейсов
- Централизованная конфигурация (NEXT_PUBLIC_API_URL)

#### State Management
- React hooks (useState, useEffect) для локального стейта
- Server Components для серверных данных
- Нет глобального state manager на начальном этапе (KISS)

## 5. TypeScript конфигурация

### Strict Mode настройки:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### Path Aliases:
- `@/*` - маппинг на `src/*`
- Позволяет импорты: `import { api } from "@/lib/api"`

### Принципы:
- Все типы явные, никаких any
- Типы API синхронизированы с backend
- Типы для всех пропсов компонентов
- Интерфейсы для объектов данных

## 6. Инструменты качества кода

### ESLint
Правила:
- `next/core-web-vitals` - базовые правила Next.js
- `@typescript-eslint/recommended` - правила для TypeScript
- `eslint-plugin-simple-import-sort` - сортировка импортов

### Prettier
Настройки:
- Автоматическое форматирование при сохранении
- Consistent code style
- Интеграция с ESLint

### TypeScript Compiler
- `tsc --noEmit` для проверки типов без сборки
- Строгий режим проверки
- Проверка перед коммитом

### Команды проверки качества:
- `make frontend-lint` - проверка ESLint
- `make frontend-type-check` - проверка типов TypeScript
- `make frontend-format` - форматирование Prettier
- `make frontend-quality` - полная проверка качества

## 7. Стилизация

### Tailwind CSS
- Utility-first подход
- Responsive дизайн (sm, md, lg, xl breakpoints)
- Dark mode support (будет добавлено позже)
- Custom theme в tailwind.config.ts

### shadcn/ui
- Компоненты на базе Radix UI
- Полностью кастомизируемые
- Копируются в проект (не npm пакет)
- Согласованный дизайн

### CSS Variables
- Цвета через CSS переменные
- Легкое переключение тем
- Централизованная конфигурация в globals.css

## 8. API Интеграция

### Backend API
- FastAPI на `http://localhost:8000`
- Mock API для разработки (FE-SP-1)
- Real API в будущем (FE-SP-5)

### CORS
- Уже настроено на backend (allow_origins=["*"] для dev)
- В production будут указаны конкретные origins

### Типизация
- Pydantic модели (Python) → TypeScript интерфейсы
- Одинаковая структура данных на backend и frontend
- Автоматическая валидация типов

### Обработка ошибок
- Try-catch блоки в API клиенте
- Логирование ошибок в консоль
- Показ ошибок пользователю через UI

## 9. Тестирование (FE-SP-3)

### Принципы тестирования:
- Unit-тесты для утилит и хелперов
- Component тесты для UI компонентов
- Integration тесты для API клиента
- E2E тесты для критических путей (опционально)

### Инструменты (будут добавлены в FE-SP-3):
- **Vitest** - быстрый unit-test runner
- **React Testing Library** - тестирование компонентов
- **MSW (Mock Service Worker)** - мокирование API

### Покрытие:
- Цель: 80%+ coverage
- Фокус на критичной логике
- Обязательно тесты для API клиента

## 10. Environment Variables

### Переменные окружения:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Принципы:
- Все публичные переменные с префиксом `NEXT_PUBLIC_`
- `.env.local` - локальные настройки (не в git)
- `.env.local.example` - пример конфигурации (в git)
- Секреты не хранятся в frontend коде

## 11. Процесс разработки

### Запуск разработки:
```bash
make frontend-install  # Установка зависимостей
make frontend-dev      # Запуск dev сервера
```

### Проверка качества:
```bash
make frontend-lint        # Линтинг
make frontend-type-check  # Проверка типов
make frontend-format      # Форматирование
make frontend-quality     # Полная проверка
```

### Сборка:
```bash
make frontend-build    # Production build
```

## 12. Что НЕ делать

❌ Использовать any типы
❌ Игнорировать TypeScript ошибки
❌ Создавать глобальный state без необходимости
❌ Смешивать Server и Client компоненты без понимания
❌ Хардкодить API URL и конфигурацию
❌ Игнорировать ошибки линтера
❌ Коммитить код без проверки качества
❌ Создавать сложные абстракции без необходимости

---

**Помни**:
- Простота > Сложность
- Типобезопасность > Any типы
- Компоненты > Дублирование
- Качество > Скорость
- `make frontend-quality` перед каждым коммитом

