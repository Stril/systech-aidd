# 🐛 Исправление проблемы Dashboard SSR

**Дата:** 18.10.2025
**Спринт:** D-SP-1 (Basic Docker Setup)
**Проблема:** Dashboard показывал ошибку "Failed to load dashboard" при первом запуске

---

## 📋 Описание проблемы

### Симптомы
При открытии `http://localhost:3000/dashboard` пользователь видел ошибку:
```
Failed to load dashboard
Network error: fetch failed
Make sure the API server is running at http://localhost:8000
```

### Контекст
- Все Docker контейнеры работали корректно (Bot, API, Frontend)
- API был доступен и отвечал на запросы (`http://localhost:8000/api/stats`)
- Frontend контейнер мог успешно обращаться к API изнутри (`http://api:8000`)
- Проблема воспроизводилась даже после полной пересборки контейнеров

---

## 🔍 Процесс диагностики

### Шаг 1: Проверка доступности API
```bash
# Проверка API снаружи
curl http://localhost:8000/health
# ✅ OK - API работает

# Проверка API изнутри Frontend контейнера
docker-compose exec frontend node -e "fetch('http://api:8000/health').then(r => r.json()).then(d => console.log('SUCCESS:', JSON.stringify(d))).catch(e => console.log('ERROR:', e.message))"
# ✅ SUCCESS: {"status":"ok"} - API доступен из контейнера
```

**Вывод:** API работает корректно, проблема не в сети.

### Шаг 2: Проверка кода
Изначально был добавлен правильный код для SSR в `frontend/src/lib/api.ts`:
```typescript
const API_URL =
  typeof window === "undefined"
    ? process.env.API_URL || "http://api:8000"  // Server-side
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // Client-side
```

**Вывод:** Код правильный, но проблема сохраняется.

### Шаг 3: Проверка сборки Next.js
Анализ логов сборки показал:
```
Route (app)                              Size     First Load JS
┌ ○ /                                    2.48 kB        98.3 kB
├ ○ /_not-found                          869 B          88.2 kB
└ ○ /dashboard                           161 kB          256 kB  # <- ○ (Static)
```

Символ `○` означает **Static Site Generation (SSG)** - страница генерируется статически **во время сборки Docker образа**.

**Ключевое открытие:** Next.js генерировал страницу `/dashboard` во время `docker build`, когда API еще не был запущен, и кэшировал страницу с ошибкой!

---

## 💡 Корневая причина

**Next.js 14** по умолчанию использует **Static Site Generation (SSG)** для всех страниц без динамических параметров в роутах.

### Что происходило:

1. **Build time** (во время `docker build frontend`):
   - Next.js пытается сгенерировать `/dashboard` статически
   - Вызывает `getStats("day")` который делает `fetch('http://api:8000/api/stats')`
   - API еще не запущен (контейнер еще не создан!)
   - Fetch падает с ошибкой "Network error: fetch failed"
   - Next.js кэширует страницу **с ошибкой** в статическую HTML

2. **Runtime** (когда пользователь открывает страницу):
   - Next.js просто отдает закэшированную статическую HTML с ошибкой
   - API уже работает, но страница уже сгенерирована со старой ошибкой
   - SSR код даже не выполняется!

### Почему полная пересборка не помогала:
- Даже после `docker-compose build --no-cache`, проблема возникала снова
- Потому что во время **каждой новой сборки** API был недоступен
- Next.js снова и снова кэшировал страницу с ошибкой

---

## ✅ Решение

### Код исправления

Добавил принудительный **Server-Side Rendering (SSR)** в файл `frontend/src/app/dashboard/page.tsx`:

```typescript
/**
 * Dashboard Page Route
 * Server Component that loads initial data and renders dashboard
 */

import { DashboardLayout } from "@/components/dashboard/dashboard-layout";
import { DashboardPage } from "@/components/dashboard/dashboard-page";
import { getStats } from "@/lib/api";

// ✅ РЕШЕНИЕ: Force dynamic rendering (SSR) instead of static generation
export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function Dashboard(): Promise<JSX.Element> {
  try {
    const initialStats = await getStats("day");

    return (
      <DashboardLayout>
        <DashboardPage initialStats={initialStats} />
      </DashboardLayout>
    );
  } catch (error) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
            <p className="text-lg font-semibold text-destructive">
              Failed to load dashboard
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {error instanceof Error ? error.message : "Unknown error"}
            </p>
          </div>
        </div>
      </DashboardLayout>
    );
  }
}
```

### Что делают эти параметры:

1. **`export const dynamic = "force-dynamic"`**
   - Принудительно включает Server-Side Rendering (SSR)
   - Страница генерируется при **каждом запросе**, а не во время сборки
   - API вызов происходит в runtime, когда API уже запущен

2. **`export const revalidate = 0`**
   - Отключает кэширование результатов
   - Гарантирует, что данные всегда свежие

### Проверка исправления

После пересборки с исправлением, лог показал:
```
Route (app)                              Size     First Load JS
┌ ○ /                                    2.48 kB        98.3 kB
├ ○ /_not-found                          869 B          88.2 kB
└ ƒ /dashboard                           161 kB          256 kB  # <- ƒ (Dynamic)!
```

Символ `ƒ` означает **Dynamic** - страница рендерится на сервере при каждом запросе.

Тест подтвердил работоспособность:
```bash
docker-compose exec frontend node -e "fetch('http://localhost:3000/dashboard').then(r => r.text()).then(t => console.log(t.includes('Activity Chart') ? 'SUCCESS' : 'ERROR'))"
# ✅ SUCCESS: Dashboard loads
```

---

## 📚 Извлеченные уроки

### 1. Next.js 14 App Router по умолчанию делает SSG
- Все страницы без `[param]` в роуте генерируются статически
- Это отличается от Pages Router, где `getServerSideProps` был явным

### 2. SSG небезопасен для страниц с внешними зависимостями
- Если страница зависит от внешнего API
- И этот API может быть недоступен во время сборки
- Нужно явно использовать SSR через `dynamic = "force-dynamic"`

### 3. Docker build порядок имеет значение
- В Docker Compose сервисы собираются параллельно
- Frontend собирается когда API еще не существует
- Нельзя полагаться на доступность других сервисов во время build

### 4. Симптомы vs корневая причина
- Симптом: "Network error: fetch failed"
- Казалось: проблема с сетью/CORS/API
- На самом деле: проблема с Next.js build strategy

---

## 🔧 Альтернативные решения (не использованы)

### 1. Client-Side Rendering (CSR)
```typescript
'use client'
import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetch('/api/stats').then(r => r.json()).then(setStats)
  }, [])

  // ...
}
```
**Минусы:**
- Плохо для SEO (хотя для приватного dashboard не критично)
- Дольше First Contentful Paint
- Пользователь видит loading state

### 2. Static Generation с revalidation
```typescript
export const revalidate = 60 // Revalidate every 60 seconds
```
**Минусы:**
- Все еще пытается генерировать статически во время build
- Та же проблема с недоступным API

### 3. Fallback страница
```typescript
export const dynamicParams = true
export const fallback = 'blocking'
```
**Минусы:**
- Только для dynamic routes с [param]
- Не применимо к /dashboard без параметров

---

## ✅ Итоговое решение

**Выбран SSR (`force-dynamic`)** как самое простое и надежное решение:
- ✅ Работает из коробки
- ✅ Нет зависимости от доступности API во время build
- ✅ Всегда свежие данные
- ✅ SEO-friendly (если понадобится)
- ✅ Минимальные изменения кода (2 строки)

**Компромисс:** Чуть медленнее TTFB (Time To First Byte) по сравнению со статической страницей, но для dashboard с аутентификацией это приемлемо.

---

## 📝 Команды для воспроизведения

```bash
# 1. Проверка проблемы (до исправления)
docker-compose up --build
# Открыть http://localhost:3000/dashboard
# Увидеть ошибку "Failed to load dashboard"

# 2. Проверка решения (после исправления)
# Добавить в frontend/src/app/dashboard/page.tsx:
# export const dynamic = "force-dynamic";
# export const revalidate = 0;

# Пересобрать
docker-compose stop frontend
docker-compose rm -f frontend
docker image rm systech-aidd-1-frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# 3. Проверить что работает
docker-compose exec frontend node -e "fetch('http://localhost:3000/dashboard').then(r => r.text()).then(t => console.log(t.includes('Activity Chart') ? 'SUCCESS: Dashboard loads' : 'ERROR: Still shows error'))"
# Ожидаем: SUCCESS: Dashboard loads

# 4. Открыть в браузере
# http://localhost:3000/dashboard
# Должен показать рабочий dashboard с графиками
```

---

## 📚 Полезные ссылки

- [Next.js 14 App Router - Dynamic Rendering](https://nextjs.org/docs/app/building-your-application/rendering/server-components#dynamic-rendering)
- [Next.js Route Segment Config - dynamic](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config#dynamic)
- [Next.js Route Segment Config - revalidate](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config#revalidate)

---

**Автор:** AI Assistant
**Дата:** 18.10.2025
**Статус:** ✅ Решено и протестировано

