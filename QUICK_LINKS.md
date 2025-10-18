# Быстрые ссылки для проверки Спринта D-SP-2

## 🔍 Где найти Docker образы

### GitHub Packages (основное место)
```
https://github.com/Stril?tab=packages
```

**Что искать:**
- `systech-aidd-bot`
- `systech-aidd-api`
- `systech-aidd-frontend`

---

## 📊 Проверка статуса

### Actions (проверка workflow)
```
https://github.com/Stril/systech-aidd/actions
```

**Что проверить:**
- Последний run с commit `47af2bf` или `938afc5`
- Все 3 jobs должны быть ✅ зеленые

### Pull Requests
```
https://github.com/Stril/systech-aidd/pulls
```

**Что сделать:**
- Если все jobs зеленые → Merge PR
- Используйте "Squash and merge"

---

## 🐳 Команды для работы с образами

### Скачать образы (после публикации)
```bash
# Bot
docker pull ghcr.io/stril/systech-aidd-bot:latest

# API
docker pull ghcr.io/stril/systech-aidd-api:latest

# Frontend
docker pull ghcr.io/stril/systech-aidd-frontend:latest
```

### Проверить загруженные образы
```powershell
docker images | Select-String "systech-aidd"
```

### Запустить через docker-compose (с registry образами)
```powershell
# 1. Отредактируйте файл (замените <owner> на stril)
(Get-Content docker-compose.registry.yml) -replace '<owner>', 'stril' | Set-Content docker-compose.registry.yml

# 2. Pull образов
docker-compose -f docker-compose.registry.yml pull

# 3. Запуск
docker-compose -f docker-compose.registry.yml up -d

# 4. Проверка
docker-compose -f docker-compose.registry.yml ps
```

---

## 🔓 Сделать образы публичными

Для каждого образа на странице Packages:

1. Откройте образ (кликните на имя)
2. **Package settings** (справа вверху)
3. Scroll down → **"Danger Zone"**
4. **"Change visibility"** → **"Public"**
5. Подтвердите

---

## ⚙️ Настройка Workflow permissions (если нужно)

```
https://github.com/Stril/systech-aidd/settings/actions
```

**Settings → Actions → General → Workflow permissions:**
- Выбрать: "Read and write permissions"
- Включить: "Allow GitHub Actions to create and approve pull requests"
- Save

---

## 📋 Полный чеклист

См. файл: `devops/doc/D-SP-2-COMPLETION-CHECKLIST.md`

---

## ❓ Troubleshooting

### Образов нет в Packages
**Причина:** PR не смержен в main или workflow не выполнился

**Решение:**
1. Проверьте что PR смержен
2. Проверьте что workflow на main выполнился успешно
3. Подождите 3-5 минут после merge

### Ошибка "denied" при pull
**Причина:** Образы приватные

**Решение:**
Сделайте образы публичными (см. раздел выше)

### Workflow падает
**Причина:** Зависит от конкретной ошибки

**Решение:**
1. Откройте логи упавшего job
2. Найдите красную строку с ошибкой
3. Проверьте что все файлы закоммичены
4. Особенно проверьте `frontend/src/lib/formatters.ts`

---

**Последнее обновление:** 18 октября 2025
**Commit:** 938afc5

