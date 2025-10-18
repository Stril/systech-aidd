# Frontend Sprints

Документация по спринтам разработки Frontend.

## Спринты

### Sprint 2: Инициализация Frontend проекта

**Статус:** ✅ Завершено
**Дата:** 17 октября 2025
**Документ:** [SPRINT2_IMPLEMENTATION.md](SPRINT2_IMPLEMENTATION.md)

#### Что было сделано

- Создан Next.js 14 проект с App Router
- Настроен TypeScript strict mode
- Установлен и настроен shadcn/ui (New York style)
- Созданы API типы синхронизированные с backend
- Реализован типизированный API клиент
- Создана базовая страница с проверкой API
- Добавлены Makefile команды для frontend
- Создана comprehensive документация

#### Технологии

- Next.js 14 + React 18
- TypeScript 5
- Tailwind CSS 3.4
- shadcn/ui
- pnpm

---

### Sprint 4: AI Chat компонент

**Статус:** ✅ Завершено
**Дата:** 18 октября 2025
**Документ:** [SPRINT4_SUMMARY.md](SPRINT4_SUMMARY.md)

#### Что было сделано

**Backend:**
- API Models для chat сессий
- Session Manager с in-memory storage
- Text2SQL Handler для admin режима
- Chat Handler для обработки сообщений
- API endpoints: создание сессии, отправка сообщения, удаление

**Frontend:**
- TypeScript типы для chat
- Chat API client
- UI компоненты: ChatWindow, ChatMessage, ModeToggle, FloatingChatButton
- Интеграция в Dashboard
- Два режима: Normal и Admin (text2sql)

**Testing:**
- 19 новых тестов (189 total)
- Coverage 98%+

---

### Sprint FE-SP-4: Переход на Real API

**Статус:** ✅ Завершено
**Дата:** 17 октября 2025
**Документ:** [SPRINT_FE-SP-4_SUMMARY.md](SPRINT_FE-SP-4_SUMMARY.md)

#### Что было сделано

- Реализован `RealStatCollector` работающий с SQLite БД
- Добавлена конфигурация переключения Mock/Real через `.env`
- Обновлен API entrypoint с условной инициализацией
- Созданы 17 unit тестов (170 passed, 98.56% coverage)
- Оптимизированные SQL запросы с индексами
- Поддержка soft delete

#### SQL запросы

- Summary метрики
- Activity chart по часам/дням
- Recent conversations
- Top users

---

### Sprint FE-SP-6: Авторизация пользователя

**Статус:** ✅ Завершено
**Дата:** 18 октября 2025
**Документ:** [SPRINT_FE-SP-6_SUMMARY.md](SPRINT_FE-SP-6_SUMMARY.md)

#### Что было сделано

**Backend:**
- Утилиты для работы с username (`user_utils.py`)
- Обновлены модели с username и user_id
- Интеграция SQLiteStorage для web-пользователей
- Web-пользователи с отрицательными user_id

**Frontend:**
- User storage утилиты (localStorage)
- UserNameBadge компонент с inline редактированием
- Автогенерация username при первом открытии
- Разные usernames для normal/admin режимов

**Testing:**
- 9 новых тестов (198 passed)
- Coverage 97.35%

---

### Sprint FE-SP-7: Хранение диалогов

**Статус:** ✅ Завершено
**Дата:** 18 октября 2025
**Документ:** [SPRINT_FE-SP-7_SUMMARY.md](SPRINT_FE-SP-7_SUMMARY.md)

#### Что было сделано

- Интеграция Storage в ChatSessionManager
- Сохранение пользовательских сообщений в БД
- Автоматическое создание conversations
- Только user messages сохраняются (не ответы assistant)
- 6 новых тестов (204 passed)
- Coverage 97.35%

## Технологический стек

| Технология | Назначение |
|------------|------------|
| Next.js 14 | React framework с App Router |
| React 18 | UI библиотека |
| TypeScript 5 | Типизация |
| Tailwind CSS | Styling framework |
| shadcn/ui | UI компоненты |
| pnpm | Пакетный менеджер |
| framer-motion | Анимации |

## Метрики (суммарно)

- Спринтов завершено: 5
- Файлов создано/изменено: ~40+
- Строк кода: ~2000+
- Тестов добавлено: ~50+
- Coverage: 97%+

## Связанные документы

- [Frontend Roadmap](../../../frontend/doc/frontend-roadmap.md)
- [Frontend Vision](../../../frontend/doc/frontend-vision.md)
- [Frontend README](../../../frontend/README.md)
- [API README](../../../api/README.md)

---

**Следующие спринты:** См. [Frontend Roadmap](../../../frontend/doc/frontend-roadmap.md)

