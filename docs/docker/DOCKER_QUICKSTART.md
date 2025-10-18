# 🐳 Docker Quick Start Guide

## Результат Sprint D-SP-1

Проект полностью контейнеризован! Все 3 сервиса (Bot, API, Frontend) запускаются одной командой.

---

## 🚀 Запуск за 3 шага

### 1. Создайте .env файл

```bash
cp .env.example .env
```

Отредактируйте `.env` и заполните **обязательные** токены:
- `TELEGRAM_BOT_TOKEN` - получить у [@BotFather](https://t.me/BotFather)
- `OPENAI_API_KEY` - получить на [OpenRouter.ai](https://openrouter.ai/)

### 2. Запустите все сервисы

```bash
docker-compose up --build
```

**Первый запуск займет 5-10 минут:**
- Скачивание base образов
- Установка зависимостей
- Сборка frontend
- Применение миграций

**Последующие запуски:** ~30 секунд

### 3. Проверьте доступность

- **API Documentation:** http://localhost:8000/docs
- **Frontend Dashboard:** http://localhost:3000
- **Bot:** Отправьте сообщение боту в Telegram

---

## 📊 Архитектура

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
│         ./logs (Logs)                   │
└─────────────────────────────────────────┘
```

---

## 🔧 Управление контейнерами

```bash
# Запуск в фоне
docker-compose up -d

# Просмотр логов всех сервисов
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

# Пересборка после изменений кода
docker-compose up --build
```

---

## ❓ Troubleshooting

### Порт 8000 уже занят

```bash
# Windows PowerShell
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Остановить процесс или изменить порт в docker-compose.yml
```

### Database is locked

```bash
# Перезапустить контейнеры
docker-compose restart
```

### Контейнер постоянно перезапускается

```bash
# Посмотреть логи
docker-compose logs bot

# Проверить токены в .env файле
```

### Изменения в коде не применяются

```bash
# Пересобрать образы без кэша
docker-compose build --no-cache
docker-compose up
```

---

## 📚 Полная документация

Для детального руководства см.:
- **[devops/doc/guides/docker-setup.md](devops/doc/guides/docker-setup.md)** - Полное руководство
  - Установка Docker Desktop
  - Troubleshooting (10+ проблем)
  - FAQ

- **[SPRINT_D-SP-1_SUMMARY.md](SPRINT_D-SP-1_SUMMARY.md)** - Итоги спринта
  - Что было сделано
  - Технические решения
  - Архитектурные решения

- **[README.md](README.md)** - Основная документация проекта

---

## ✅ Checklist первого запуска

- [ ] Docker Desktop установлен и запущен
- [ ] Создан `.env` файл из `.env.example`
- [ ] Заполнены `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY` в `.env`
- [ ] Выполнена команда `docker-compose up --build`
- [ ] API доступен на http://localhost:8000/docs
- [ ] Frontend доступен на http://localhost:3000
- [ ] Bot отвечает на сообщения в Telegram

---

## 🎯 Следующие шаги

После успешного запуска:
1. Изучите API документацию: http://localhost:8000/docs
2. Откройте Frontend дашборд: http://localhost:3000
3. Протестируйте бота в Telegram
4. Просмотрите логи для понимания работы системы

---

**Sprint:** D-SP-1 Basic Docker Setup
**Status:** ✅ Complete
**Date:** 18 октября 2025

