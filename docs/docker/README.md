# Docker Documentation

Полная документация по работе с Docker в проекте systech-aidd-1.

## 📚 Документы

### [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

**Быстрый старт за 3 шага** - для тех, кто хочет сразу запустить проект.

Содержание:
- Создание `.env` файла
- Запуск всех сервисов одной командой
- Проверка доступности
- Основные команды управления
- Troubleshooting (краткий)

**Для кого:** Разработчики, которые хотят быстро запустить проект локально.

---

### [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)

**Решение проблем Docker** - подробное руководство по устранению ошибок.

Содержание:
- Issue #1: Dashboard "Failed to load" Error
  - Root cause анализ (Next.js SSR в Docker)
  - Решение через разные URL для server/client
  - Verification steps
  - Lessons learned

**Для кого:** Разработчики, столкнувшиеся с проблемами при запуске Docker контейнеров.

---

### [DASHBOARD_SSR_FIX.md](DASHBOARD_SSR_FIX.md)

**Детальный анализ исправления SSR проблемы** - техническая документация.

Содержание:
- Описание проблемы (симптомы, контекст)
- Процесс диагностики (3 шага)
- Корневая причина (Next.js SSG vs SSR)
- Решение (`force-dynamic`, `revalidate: 0`)
- Извлеченные уроки
- Альтернативные решения (не использованы)
- Команды для воспроизведения

**Для кого:** Разработчики, интересующиеся техническими деталями или столкнувшиеся с похожей проблемой.

---

## 🏗️ Архитектура Docker

Проект использует Docker Compose для оркестрации 3 сервисов:

```
┌─────────────────────────────────────────┐
│         docker-compose                  │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │   API    │  │   Bot    │  │Frontend││
│  │  :8000   │  │          │  │ :3000  ││
│  └────┬─────┘  └────┬─────┘  └────┬───┘│
│       │             │              │    │
│       └─────────────┴──────────────┘    │
│              Shared Volumes:            │
│         ./data (SQLite + WAL)           │
│         ./logs (Application logs)       │
│                                         │
│         Network: aidd-network           │
└─────────────────────────────────────────┘
```

### Сервисы

1. **API (FastAPI)** - порт 8000
   - Backend REST API
   - Автоматическое применение миграций
   - Health check endpoint
   - Swagger UI на `/docs`

2. **Bot (Telegram)** - без портов
   - Telegram бот для диалогов с пользователями
   - Зависит от API (запускается после API)
   - Polling mode
   - Доступ к SQLite через shared volume

3. **Frontend (Next.js)** - порт 3000
   - React приложение с dashboard и chat
   - SSR (Server-Side Rendering)
   - Подключение к API через environment variables
   - Production build

### Volumes

- `./data:/app/data` - Персистентные данные SQLite (включая WAL файлы)
- `./logs:/app/logs` - Логи всех сервисов

### Network

- `aidd-network` (bridge) - Изолированная сеть для всех контейнеров

---

## 🚀 Основные команды

```bash
# Запуск всех сервисов
docker-compose up --build

# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f api
docker-compose logs -f bot
docker-compose logs -f frontend

# Перезапуск
docker-compose restart

# Перезапуск конкретного сервиса
docker-compose restart api

# Остановка
docker-compose down

# Пересборка без кэша
docker-compose build --no-cache

# Статус контейнеров
docker-compose ps

# Выполнение команды в контейнере
docker-compose exec api bash
docker-compose exec frontend sh
```

---

## ❓ Частые проблемы

### Порт уже занят

```bash
# Windows PowerShell
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Решение: остановить процесс или изменить порт в docker-compose.yml
```

### Database is locked

```bash
# Решение: перезапустить контейнеры
docker-compose restart
```

### Dashboard показывает "Failed to load"

См. детальное решение в [DASHBOARD_SSR_FIX.md](DASHBOARD_SSR_FIX.md)

**Краткое решение:**
- Проверить environment variables в `docker-compose.yml`
- Убедиться что есть `API_URL=http://api:8000` для SSR
- Убедиться что есть `NEXT_PUBLIC_API_URL=http://localhost:8000` для browser

### Изменения кода не применяются

```bash
# Пересборка образов без кэша
docker-compose build --no-cache
docker-compose up
```

---

## 📦 Dockerfiles

### Dockerfile.bot
- Base: `python:3.11-slim`
- Package manager: `uv`
- Копируются: `src/`, `system_prompt.txt`, `pyproject.toml`
- Command: `uv run python -m src.main`

### Dockerfile.api
- Base: `python:3.11-slim`
- Package manager: `uv`
- Копируются: `api/`, `src/`, `migrations/`, `system_prompt.txt`, `text2sql_prompt.txt`
- Command: `uv run uvicorn api.main:app --host 0.0.0.0 --port 8000`
- Health check: Python urllib

### frontend/Dockerfile.frontend
- Base: `node:20-alpine`
- Package manager: `pnpm`
- Multi-step: install deps → build → serve
- Command: `pnpm start`
- Port: 3000

---

## 🔧 Environment Variables

Все переменные окружения в `.env` файле (см. `.env.example`):

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token_here

# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=openrouter/meta-llama/llama-3.1-70b-instruct

# Database
DATABASE_URL=sqlite+aiosqlite:///data/bot.db

# API
USE_MOCK_STAT_COLLECTOR=false  # true для mock данных

# Frontend (в docker-compose.yml)
NEXT_PUBLIC_API_URL=http://localhost:8000  # для browser
API_URL=http://api:8000                     # для SSR
```

---

## 📊 Метрики

**Время сборки (первый запуск):**
- API: ~11 секунд
- Bot: ~11 секунд
- Frontend: ~65 секунд
- **Итого:** ~90 секунд

**Время запуска (повторный):**
- API: ~5 секунд
- Bot: ~5 секунд
- Frontend: ~3 секунды
- **Итого:** ~13 секунд

**Размеры образов:**
- API: ~300 MB
- Bot: ~300 MB
- Frontend: ~450 MB

**Использование ресурсов (idle):**
- CPU: ~1% (API, Bot), ~0.5% (Frontend)
- Memory: ~150 MB (API), ~140 MB (Bot), ~180 MB (Frontend)

---

## 🎯 Checklist первого запуска

- [ ] Docker Desktop установлен и запущен
- [ ] Создан `.env` файл из `.env.example`
- [ ] Заполнены `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY` в `.env`
- [ ] Выполнена команда `docker-compose up --build`
- [ ] API доступен на http://localhost:8000/docs
- [ ] Frontend доступен на http://localhost:3000
- [ ] Bot отвечает на сообщения в Telegram

---

## 📚 Дополнительная документация

- [Sprint D-SP-1 Summary](../sprints/devops/SPRINT_D-SP-1_SUMMARY.md) - Полный отчет о реализации Docker setup
- [Sprint D-SP-1 Verification](../sprints/devops/SPRINT_D-SP-1_VERIFICATION.md) - Результаты тестирования
- [DevOps Roadmap](../../devops/doc/devops-roadmap.md) - План развития DevOps
- [Docker Setup Guide](../../devops/doc/guides/docker-setup.md) - Детальное руководство

---

**Sprint:** D-SP-1 Basic Docker Setup
**Status:** ✅ Complete
**Date:** 18 октября 2025

