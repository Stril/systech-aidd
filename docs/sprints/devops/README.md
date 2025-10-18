# DevOps Sprints

Документация по спринтам DevOps - контейнеризация, CI/CD, инфраструктура.

## Спринты

### Sprint D-SP-1: Basic Docker Setup

**Статус:** ✅ Завершено
**Дата:** 18 октября 2025
**Время выполнения:** 2 часа

- **[SPRINT_D-SP-1_SUMMARY.md](SPRINT_D-SP-1_SUMMARY.md)** - Полный отчет о реализации
- **[SPRINT_D-SP-1_VERIFICATION.md](SPRINT_D-SP-1_VERIFICATION.md)** - Результаты тестирования

#### 🎯 Цель спринта

Запустить все сервисы (Bot, API, Frontend) локально через `docker-compose up` одной командой для быстрого старта разработки.

#### ✅ Что было сделано

**Docker конфигурация:**
- `Dockerfile.bot` - Telegram бот (Python 3.11 + uv)
- `Dockerfile.api` - FastAPI сервис (Python 3.11 + uv)
- `frontend/Dockerfile.frontend` - Next.js приложение (Node 20 + pnpm)
- `docker-compose.yml` - оркестрация 3 сервисов
- `.dockerignore` - обновлен для WAL файлов SQLite
- `frontend/.dockerignore` - исключение ненужных файлов

**Конфигурация и настройка:**
- `.env.example` - шаблон переменных окружения
- `src/sqlite_storage.py` - connect_args для multi-process доступа
  - `timeout: 30.0` - увеличенный timeout
  - `check_same_thread: False` - для async работы

**Документация:**
- `README.md` - добавлены разделы по Docker запуску
- `devops/doc/guides/docker-setup.md` - полное руководство
- `devops/doc/plans/d-sp-1-implementation.md` - план реализации
- `devops/doc/devops-roadmap.md` - обновлен статус

#### 🏗️ Архитектура

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
└─────────────────────────────────────────┘
```

**Сервисы:**
1. **API (FastAPI)** - порт 8000
   - Автоматическое применение миграций
   - Health check endpoint
   - Доступ к SQLite через shared volume

2. **Bot (Telegram)** - без портов
   - Зависит от API
   - Polling mode для Telegram API

3. **Frontend (Next.js)** - порт 3000
   - Production build
   - Подключение к API через `NEXT_PUBLIC_API_URL`

#### 🔧 Технические решения

**SQLite Multi-Process Access:**
- WAL (Write-Ahead Logging) mode
- Параллельное чтение во время записи
- timeout: 30.0 для корректной работы
- Все WAL файлы на одном volume

**Простые Dockerfile:**
- MVP подход без multi-stage builds
- Быстрая итерация
- Оптимизация в следующем спринте

**Health Checks:**
- Python urllib вместо curl
- `python:3.11-slim` не содержит curl

#### 📊 Результаты тестирования

**Сборка контейнеров:**
- API: ~11 секунд
- Bot: ~11 секунд (кэш)
- Frontend: ~65 секунд

**Размеры образов:**
- `systech-aidd-1-api`: ~300 MB
- `systech-aidd-1-bot`: ~300 MB
- `systech-aidd-1-frontend`: ~450 MB

**Использование ресурсов:**
- CPU: ~1% (API, Bot), ~0.5% (Frontend)
- Memory: ~150 MB (API), ~140 MB (Bot), ~180 MB (Frontend)

**Проблемы и решения:**
- Отсутствие `system_prompt.txt` в API - добавлена копия в Dockerfile
- Dashboard SSR ошибка - решена через `force-dynamic` и разные URL для SSR/Client

#### ✅ Критерии успеха (все выполнены)

- ✅ Одна команда `docker-compose up` запускает все 3 сервиса
- ✅ Bot подключается к Telegram и отвечает на сообщения
- ✅ API доступен на http://localhost:8000/docs
- ✅ Frontend доступен на http://localhost:3000
- ✅ SQLite database shared между Bot и API (WAL mode)
- ✅ Логи пишутся в `./logs` volume
- ✅ `.env.example` документирует все переменные
- ✅ README содержит инструкции
- ✅ Подробная документация в `docker-setup.md`

## 🚀 Быстрый старт

```bash
# 1. Создать .env из шаблона
cp .env.example .env

# 2. Отредактировать .env и заполнить:
#    - TELEGRAM_BOT_TOKEN
#    - OPENAI_API_KEY

# 3. Запустить все сервисы
docker-compose up --build

# 4. Проверить доступность:
#    - API: http://localhost:8000/docs
#    - Frontend: http://localhost:3000
#    - Bot: отправить сообщение в Telegram
```

## 🔮 Следующие шаги

### D-SP-2: Build & Publish

- GitHub Actions для автоматической сборки
- Публикация образов в GitHub Container Registry (ghcr.io)
- Multi-stage builds для оптимизации размера
- Тегирование образов (latest, semantic versions)
- Status badges в README

## Связанные документы

- [DevOps Roadmap](../../../devops/doc/devops-roadmap.md)
- [Docker Setup Guide](../../../devops/doc/guides/docker-setup.md)
- [Docker Quickstart](../../docker/DOCKER_QUICKSTART.md)
- [Docker Troubleshooting](../../docker/DOCKER_TROUBLESHOOTING.md)

---

**Разработчик:** AI Assistant
**Sprint:** D-SP-1 Basic Docker Setup
**Status:** ✅ Complete

