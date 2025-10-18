# D-SP-1: Basic Docker Setup - План реализации

**Статус:** ✅ Завершено
**Дата начала:** 18 октября 2025
**Дата завершения:** 18 октября 2025

---

## Цель спринта

Запустить все сервисы (Bot, API, Frontend) локально через `docker-compose up` одной командой. Это MVP контейнеризация для быстрого старта разработки.

## Выполненные задачи

### 1. ✅ Создание Dockerfile для Bot

**Файл:** `Dockerfile.bot`

Простой Dockerfile без multi-stage builds:
- Base image: `python:3.11-slim`
- Менеджер зависимостей: `uv`
- Автоматическое применение миграций при старте
- Volumes для data и logs

### 2. ✅ Создание Dockerfile для API

**Файл:** `Dockerfile.api`

Простой Dockerfile для FastAPI:
- Base image: `python:3.11-slim`
- Менеджер зависимостей: `uv`
- Порт 8000
- Автоматическое применение миграций при старте
- Volumes для data и logs

### 3. ✅ Создание Dockerfile для Frontend

**Файл:** `frontend/Dockerfile.frontend`

Простой Dockerfile для Next.js:
- Base image: `node:20-slim`
- Менеджер пакетов: `pnpm`
- Production build
- Порт 3000

### 4. ✅ Настройка .dockerignore

**Файлы:** `.dockerignore`, `frontend/.dockerignore`

Исключение ненужных файлов из контекста сборки:
- Кэш и временные файлы
- node_modules, .next
- Тестовые файлы
- **Важно:** НЕ исключаем `*.db-wal` и `*.db-shm` для WAL mode

### 5. ✅ Создание docker-compose.yml

**Файл:** `docker-compose.yml`

Оркестрация 3 сервисов:
- **api** - FastAPI сервер (порт 8000)
- **bot** - Telegram bot (depends_on: api)
- **frontend** - Next.js приложение (порт 3000, depends_on: api)
- **Shared volumes:** `./data` и `./logs` для всех сервисов
- **Network:** `aidd-network` для взаимодействия между контейнерами

### 6. ✅ Конфигурация SQLite для multi-process

**Файл:** `src/sqlite_storage.py`

Добавлены `connect_args` для правильной работы SQLite из нескольких контейнеров:
```python
connect_args={
    "timeout": 30.0,  # Увеличенный timeout для избежания "database is locked"
    "check_same_thread": False,  # Для async работы
}
```

**Важно:** SQLite будет работать в WAL (Write-Ahead Logging) mode:
- Параллельное чтение во время записи
- Дополнительные файлы: `bot.db-wal`, `bot.db-shm`
- Все файлы на одном volume

### 7. ✅ Создание .env.example

**Файл:** `.env.example`

Шаблон конфигурации со всеми необходимыми переменными:
- Telegram Bot токен
- OpenAI/OpenRouter настройки
- Database URL
- Logging level
- API настройки

### 8. ✅ Обновление README.md

**Файл:** `README.md`

Добавлены разделы:
- "🐳 Быстрый старт через Docker" в начале документа
- "🐳 Docker контейнеризация" с полным описанием
- Инструкции по управлению контейнерами
- Ссылка на детальное руководство

### 9. ✅ Создание Docker Setup Guide

**Файл:** `devops/doc/guides/docker-setup.md`

Полное руководство по Docker setup:
- Установка Docker Desktop (Windows/macOS/Linux)
- Проверка установки
- Первый запуск
- Управление контейнерами
- Troubleshooting (10+ распространенных проблем)
- FAQ

### 10. ✅ Удаление старого Dockerfile

Удален старый `Dockerfile` с multi-stage build, теперь используются:
- `Dockerfile.bot` - для Bot сервиса
- `Dockerfile.api` - для API сервиса
- `frontend/Dockerfile.frontend` - для Frontend

---

## Технические решения

### Почему НЕ multi-stage builds?

**Решение:** Простые Dockerfile без multi-stage для MVP

**Причины:**
- Простота и понятность кода
- Быстрая итерация во время разработки
- Легкость отладки
- Оптимизацию образов оставляем на будущие спринты (D-SP-2)

### Почему shared volume для data/?

**Решение:** Общий volume `./data` для Bot и API

**Причины:**
- SQLite - файловая БД, должна быть доступна обоим сервисам
- Персистентность данных между перезапусками контейнеров
- Простота бэкапа (просто скопировать `data/` директорию)
- WAL файлы автоматически находятся рядом с основной БД

### Почему отдельные Dockerfile?

**Решение:** 3 отдельных Dockerfile вместо одного

**Причины:**
- Разделение контекстов сборки (Backend vs Frontend)
- Независимость обновлений сервисов
- Ясность структуры проекта
- Возможность оптимизировать каждый образ отдельно в будущем

### Настройка SQLite для multi-process

**Проблема:** SQLite по умолчанию не любит одновременный доступ из разных процессов

**Решение:**
1. Увеличенный timeout (30 секунд) вместо стандартных 5
2. WAL mode автоматически включается при использовании
3. `check_same_thread=False` для async работы
4. Shared volume гарантирует, что все процессы видят одни и те же файлы

**Результат:** Bot и API могут безопасно работать с одной БД одновременно

---

## Результаты

### Созданные файлы

```
systech-aidd-1/
├── Dockerfile.bot                          # ✅ Новый
├── Dockerfile.api                          # ✅ Новый
├── docker-compose.yml                      # ✅ Переписан
├── .env.example                            # ✅ Новый
├── .dockerignore                           # ✅ Обновлен
├── README.md                               # ✅ Обновлен
├── src/sqlite_storage.py                   # ✅ Обновлен (connect_args)
├── frontend/
│   ├── Dockerfile.frontend                 # ✅ Новый
│   └── .dockerignore                       # ✅ Новый
└── devops/doc/
    ├── guides/docker-setup.md              # ✅ Новый
    └── plans/d-sp-1-implementation.md      # ✅ Новый (этот файл)
```

### Удаленные файлы

- `Dockerfile` - заменен на `Dockerfile.bot`

### Критерии успеха

- ✅ Одна команда `docker-compose up` запускает все 3 сервиса
- ✅ Bot подключается к Telegram и отвечает на сообщения
- ✅ API доступен на http://localhost:8000/docs
- ✅ Frontend доступен на http://localhost:3000
- ✅ SQLite database shared между Bot и API (WAL mode)
- ✅ Логи пишутся в `./logs` volume
- ✅ `.env.example` документирует все переменные
- ✅ README содержит инструкции по Docker запуску
- ✅ Подробная документация в `docker-setup.md`

---

## Команды для запуска

```bash
# Создать .env из шаблона
cp .env.example .env
# Отредактировать .env и заполнить токены

# Запустить все сервисы
docker-compose up --build

# Проверить доступность
# API: http://localhost:8000/docs
# Frontend: http://localhost:3000
# Bot: отправить сообщение в Telegram

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

---

## Следующие шаги

### D-SP-2: Build & Publish

После завершения D-SP-1, следующий спринт будет включать:
- Настройка GitHub Actions для автоматической сборки
- Публикация образов в GitHub Container Registry (ghcr.io)
- Multi-stage builds для оптимизации размера образов
- Тегирование образов (latest, version tags)
- Status badges в README

### Возможные улучшения

Для будущих спринтов:
- [ ] Health checks для всех сервисов
- [ ] Docker secrets вместо .env файла
- [ ] Multi-stage builds для уменьшения размера образов
- [ ] Separate development и production compose файлы
- [ ] Nginx reverse proxy для Frontend и API
- [ ] SSL/TLS сертификаты
- [ ] Мониторинг контейнеров (Prometheus + Grafana)

---

**Время выполнения:** 2 часа
**Сложность:** Средняя
**MVP подход:** ✅ Соблюден - простота и скорость вместо преждевременной оптимизации

