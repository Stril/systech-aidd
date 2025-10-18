# 🐳 Шпаргалка команд Docker для Спринта D-SP-2

## 📊 Проверка статуса

### Проверить запущенные контейнеры
```powershell
docker-compose -f docker-compose.registry.yml ps
```

### Посмотреть логи
```powershell
# Все сервисы
docker-compose -f docker-compose.registry.yml logs

# Конкретный сервис
docker-compose -f docker-compose.registry.yml logs api
docker-compose -f docker-compose.registry.yml logs bot
docker-compose -f docker-compose.registry.yml logs frontend

# Следить за логами в реальном времени
docker-compose -f docker-compose.registry.yml logs -f api
```

### Проверить образы
```powershell
docker images | Select-String "systech-aidd"
```

---

## ▶️ Управление контейнерами

### Запустить контейнеры
```powershell
docker-compose -f docker-compose.registry.yml up -d
```

### Остановить контейнеры
```powershell
docker-compose -f docker-compose.registry.yml down
```

### Перезапустить контейнеры
```powershell
docker-compose -f docker-compose.registry.yml restart
```

### Перезапустить конкретный сервис
```powershell
docker-compose -f docker-compose.registry.yml restart api
```

---

## 🔄 Обновление образов

### Скачать новые версии образов
```powershell
docker-compose -f docker-compose.registry.yml pull
```

### Пересоздать контейнеры с новыми образами
```powershell
docker-compose -f docker-compose.registry.yml up -d --force-recreate
```

### Полный цикл обновления
```powershell
# 1. Остановить контейнеры
docker-compose -f docker-compose.registry.yml down

# 2. Скачать новые образы
docker-compose -f docker-compose.registry.yml pull

# 3. Запустить с новыми образами
docker-compose -f docker-compose.registry.yml up -d
```

---

## 🔍 Диагностика

### Зайти в контейнер
```powershell
docker exec -it aidd-api bash
docker exec -it aidd-bot bash
docker exec -it aidd-frontend sh
```

### Проверить health check
```powershell
docker inspect aidd-api | Select-String "Health"
```

### Проверить переменные окружения
```powershell
docker exec aidd-api env
```

### Проверить использование ресурсов
```powershell
docker stats
```

---

## 🧹 Очистка

### Удалить контейнеры
```powershell
docker-compose -f docker-compose.registry.yml down
```

### Удалить контейнеры и volumes
```powershell
docker-compose -f docker-compose.registry.yml down -v
```

### Удалить старые образы
```powershell
docker image prune -a
```

### Полная очистка Docker
```powershell
# ОСТОРОЖНО! Удалит ВСЕ неиспользуемые ресурсы
docker system prune -a --volumes
```

---

## 🌐 Проверка работы сервисов

### API
```powershell
# Health check
Invoke-WebRequest -Uri http://localhost:8000/health

# Swagger UI
start http://localhost:8000/docs
```

### Frontend
```powershell
# Home page
Invoke-WebRequest -Uri http://localhost:3000

# Открыть в браузере
start http://localhost:3000
start http://localhost:3000/dashboard
```

### Bot
```powershell
# Проверить логи
docker logs aidd-bot --tail 50
```

---

## 🔄 Переключение между режимами

### Локальная сборка
```powershell
docker-compose up --build -d
```

### Registry образы
```powershell
docker-compose -f docker-compose.registry.yml up -d
```

### Override (если настроен)
```powershell
# Использует docker-compose.yml + docker-compose.override.yml
docker-compose up -d
```

---

## 📦 Работа с конкретными образами

### Скачать конкретную версию
```powershell
docker pull ghcr.io/stril/systech-aidd-bot:sha-abc1234
```

### Запустить конкретную версию
```yaml
# В docker-compose.registry.yml измените:
image: ghcr.io/stril/systech-aidd-bot:sha-abc1234
```

---

## 🐛 Troubleshooting

### Контейнер не запускается
```powershell
# 1. Посмотреть логи
docker-compose -f docker-compose.registry.yml logs api

# 2. Проверить .env файл
cat .env

# 3. Проверить порты
netstat -an | Select-String "8000"
netstat -an | Select-String "3000"

# 4. Пересоздать контейнер
docker-compose -f docker-compose.registry.yml up -d --force-recreate api
```

### Ошибка "port already allocated"
```powershell
# Найти процесс на порту
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Остановить конфликтующий контейнер
docker-compose down
```

### Образ не скачивается
```powershell
# Проверить доступность registry
docker pull ghcr.io/stril/systech-aidd-bot:latest

# Если denied - образы приватные, нужно сделать их публичными:
# GitHub → Packages → systech-aidd-bot → Package settings → Change visibility → Public
```

### База данных не мигрирована
```powershell
# Выполнить миграции вручную
docker exec -it aidd-api alembic upgrade head
```

---

## 📝 Полезные алиасы (опционально)

Добавьте в PowerShell profile (`$PROFILE`):

```powershell
# Docker Compose shortcuts
function dc-up { docker-compose -f docker-compose.registry.yml up -d }
function dc-down { docker-compose -f docker-compose.registry.yml down }
function dc-logs { docker-compose -f docker-compose.registry.yml logs -f $args }
function dc-ps { docker-compose -f docker-compose.registry.yml ps }
function dc-pull { docker-compose -f docker-compose.registry.yml pull }
function dc-restart { docker-compose -f docker-compose.registry.yml restart $args }

# Health checks
function check-api { Invoke-WebRequest -Uri http://localhost:8000/health }
function check-frontend { Invoke-WebRequest -Uri http://localhost:3000 }

# Browser shortcuts
function open-api { start http://localhost:8000/docs }
function open-frontend { start http://localhost:3000 }
function open-dashboard { start http://localhost:3000/dashboard }
```

**Использование после добавления:**
```powershell
dc-up           # Запустить
dc-logs api     # Логи API
dc-ps           # Статус
check-api       # Проверка API
open-api        # Открыть Swagger
```

---

**Создано:** 18 октября 2025  
**Спринт:** D-SP-2 - Build & Publish  
**Версия:** 1.0

