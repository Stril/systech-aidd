# 🐳 Руководство по Docker Setup

## Введение

Это руководство поможет вам настроить Docker окружение для локальной разработки проекта AIDD. После настройки вы сможете запустить все сервисы (Bot, API, Frontend) одной командой `docker-compose up`.

---

## Предварительные требования

### Установка Docker Desktop

**Windows:**
1. Скачайте [Docker Desktop для Windows](https://www.docker.com/products/docker-desktop/)
2. Запустите установщик и следуйте инструкциям
3. Перезагрузите компьютер после установки
4. Запустите Docker Desktop из меню Пуск

**macOS:**
1. Скачайте [Docker Desktop для Mac](https://www.docker.com/products/docker-desktop/)
2. Перетащите Docker.app в папку Applications
3. Запустите Docker из папки Applications
4. Следуйте инструкциям на экране

**Linux (Ubuntu/Debian):**
```bash
# Обновить пакеты
sudo apt-get update

# Установить зависимости
sudo apt-get install ca-certificates curl gnupg

# Добавить Docker GPG ключ
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Добавить Docker репозиторий
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Проверка установки

```bash
# Проверить версию Docker
docker --version
# Ожидается: Docker version 24.0.0 или выше

# Проверить версию Docker Compose
docker compose version
# Ожидается: Docker Compose version v2.20.0 или выше

# Проверить работу Docker
docker run hello-world
# Должен скачать и запустить тестовый контейнер
```

---

## Первый запуск

### 1. Подготовка конфигурации

```bash
# Перейти в корень проекта
cd systech-aidd-1

# Создать .env файл из шаблона
cp .env.example .env

# Отредактировать .env файл
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Обязательно заполните:**
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота (получить у @BotFather)
- `OPENAI_API_KEY` - API ключ OpenRouter (получить на openrouter.ai)

### 2. Запуск всех сервисов

```bash
# Сборка и запуск в режиме foreground (с выводом логов)
docker-compose up --build

# Или запуск в фоновом режиме (detached)
docker-compose up -d --build
```

**Первый запуск займет 5-10 минут:**
- Скачивание base образов (python:3.11-slim, node:20-slim)
- Установка зависимостей через uv и pnpm
- Сборка frontend приложения
- Применение миграций базы данных

### 3. Проверка работоспособности

После запуска проверьте доступность сервисов:

**API:**
```bash
curl http://localhost:8000/health
# Или откройте в браузере: http://localhost:8000/docs
```

**Frontend:**
```
Откройте в браузере: http://localhost:3000
```

**Bot:**
```
Отправьте сообщение вашему боту в Telegram
Проверьте логи: docker-compose logs -f bot
```

---

## Управление контейнерами

### Основные команды

```bash
# Запустить все сервисы
docker-compose up

# Запустить в фоновом режиме
docker-compose up -d

# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (ОСТОРОЖНО: удалит БД!)
docker-compose down -v

# Перезапустить сервисы
docker-compose restart

# Перезапустить конкретный сервис
docker-compose restart api

# Остановить конкретный сервис
docker-compose stop bot

# Запустить остановленный сервис
docker-compose start bot
```

### Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs

# Логи с автообновлением (follow)
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs api
docker-compose logs bot
docker-compose logs frontend

# Последние 100 строк логов
docker-compose logs --tail=100 api
```

### Пересборка после изменений

```bash
# Пересборка всех сервисов
docker-compose up --build

# Пересборка конкретного сервиса
docker-compose up --build api

# Принудительная пересборка без кэша
docker-compose build --no-cache
docker-compose up
```

### Выполнение команд внутри контейнеров

```bash
# Открыть shell в контейнере
docker-compose exec api bash
docker-compose exec bot bash

# Выполнить команду
docker-compose exec api alembic current
docker-compose exec bot python -c "print('Hello')"

# Запустить тесты API
docker-compose exec api pytest tests/
```

---

## Troubleshooting

### Порт уже занят

**Проблема:**
```
Error: bind: address already in use
```

**Решение:**
```bash
# Найти процесс, занимающий порт 8000
# Windows PowerShell:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Остановить процесс или изменить порт в docker-compose.yml:
ports:
  - "8001:8000"  # Используем 8001 вместо 8000
```

### Database is locked

**Проблема:**
```
sqlite3.OperationalError: database is locked
```

**Решение:**
1. Убедитесь, что `src/sqlite_storage.py` содержит правильные `connect_args`:
   ```python
   connect_args={
       "timeout": 30.0,
       "check_same_thread": False,
   }
   ```
2. Перезапустите контейнеры:
   ```bash
   docker-compose restart
   ```

### Недостаточно места на диске

**Проблема:**
```
Error: no space left on device
```

**Решение:**
```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes
docker volume prune

# Удалить всё неиспользуемое (осторожно!)
docker system prune -a --volumes
```

### Контейнер постоянно перезапускается

**Проблема:**
Контейнер перезапускается каждые несколько секунд

**Решение:**
```bash
# Посмотреть логи для диагностики
docker-compose logs bot

# Типичные причины:
# 1. Неправильный TELEGRAM_BOT_TOKEN в .env
# 2. Неправильный OPENAI_API_KEY в .env
# 3. Ошибка в коде приложения
# 4. Недоступна база данных
```

### Проблемы с правами доступа (Linux)

**Проблема:**
```
Permission denied: '/app/data/bot.db'
```

**Решение:**
```bash
# Дать права на директории data и logs
sudo chown -R $USER:$USER data/ logs/

# Или добавить пользователя в группу docker
sudo usermod -aG docker $USER
# Затем выйти и войти снова
```

### Изменения в коде не применяются

**Проблема:**
Внесли изменения в код, но они не отображаются в контейнере

**Решение:**
```bash
# Пересобрать образы без кэша
docker-compose build --no-cache

# Затем запустить
docker-compose up
```

### Миграции не применяются

**Проблема:**
База данных не обновлена до последней версии

**Решение:**
```bash
# Применить миграции вручную
docker-compose exec api alembic upgrade head
docker-compose exec bot alembic upgrade head

# Проверить текущую версию
docker-compose exec api alembic current
```

---

## FAQ

### Как посмотреть какие контейнеры запущены?

```bash
docker-compose ps
# Или
docker ps
```

### Как полностью удалить все контейнеры и данные?

```bash
# Остановить и удалить контейнеры, сети, volumes
docker-compose down -v

# Удалить образы
docker-compose down --rmi all

# ВНИМАНИЕ: это удалит базу данных!
```

### Как сделать бэкап базы данных?

```bash
# Скопировать файл БД из контейнера
docker cp aidd-api:/app/data/bot.db ./backup_bot_$(date +%Y%m%d).db

# Или просто скопировать из локальной директории
cp data/bot.db backups/bot_$(date +%Y%m%d).db
```

### Как восстановить базу данных из бэкапа?

```bash
# Остановить сервисы
docker-compose down

# Восстановить из бэкапа
cp backups/bot_20251018.db data/bot.db

# Запустить сервисы
docker-compose up -d
```

### Можно ли запустить только один сервис?

```bash
# Запустить только API
docker-compose up api

# Запустить только Bot
docker-compose up bot

# Запустить только Frontend
docker-compose up frontend
```

### Как обновить зависимости в контейнере?

```bash
# Обновить pyproject.toml или package.json
# Затем пересобрать:
docker-compose build --no-cache
docker-compose up
```

### Как узнать IP адрес контейнера?

```bash
docker inspect aidd-api | grep IPAddress
# Или
docker-compose exec api hostname -i
```

---

## Следующие шаги

После успешного запуска:
1. Протестируйте бота в Telegram
2. Откройте API документацию: http://localhost:8000/docs
3. Откройте Frontend дашборд: http://localhost:3000
4. Изучите логи для понимания работы системы

## Полезные ссылки

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/)
- [Основной README проекта](../../../README.md)
- [DevOps Roadmap](../devops-roadmap.md)

---

**Версия:** 1.0.0
**Дата:** 18 октября 2025
**Sprint:** D-SP-1 Basic Docker Setup

