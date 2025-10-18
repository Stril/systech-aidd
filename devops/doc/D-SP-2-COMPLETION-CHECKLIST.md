# Чеклист завершения Спринта D-SP-2

**Дата:** 18 октября 2025  
**Статус:** ⏳ В процессе проверки  
**PR:** https://github.com/Stril/systech-aidd/pull/[номер]

---

## ✅ Этап 1: Проверка успешности workflow (СЕЙЧАС)

### 1.1 Откройте GitHub Actions

```
https://github.com/Stril/systech-aidd/actions
```

### 1.2 Найдите последний run

**Commit:** `47af2bf - fix: add missing formatters.ts and update .gitignore`

### 1.3 Проверьте статус всех 3 jobs

- [ ] `build-and-push (bot)` - зеленый ✅
- [ ] `build-and-push (api)` - зеленый ✅  
- [ ] `build-and-push (frontend)` - зеленый ✅

**Если все зеленые** → переходите к Этапу 2  
**Если что-то красное** → смотрите логи, сообщите об ошибке

---

## ✅ Этап 2: Merge Pull Request в main

### 2.1 Откройте PR

```
https://github.com/Stril/systech-aidd/pulls
```

### 2.2 Убедитесь что CI checks прошли

Внизу PR должно быть:
```
✅ All checks have passed
```

### 2.3 Merge PR

1. Нажмите **"Squash and merge"** (рекомендуется)
2. Отредактируйте commit message если нужно:
   ```
   ci: implement D-SP-2 GitHub Actions CI/CD pipeline (#[номер])
   ```
3. Нажмите **"Confirm squash and merge"**
4. Нажмите **"Delete branch"** (удалить feature ветку)

### 2.4 Дождитесь автоматического workflow на main

После merge автоматически запустится workflow:
- Build всех 3 образов
- **Публикация в ghcr.io** (это происходит ТОЛЬКО на main!)

⏳ **Подождите 3-5 минут**

---

## ✅ Этап 3: Настройка публичного доступа к образам

### 3.1 Откройте GitHub Packages

```
https://github.com/Stril?tab=packages
```

### 3.2 Убедитесь что появились 3 образа

- [ ] `systech-aidd-bot`
- [ ] `systech-aidd-api`
- [ ] `systech-aidd-frontend`

### 3.3 Сделайте каждый образ публичным

**Для каждого из 3 образов:**

1. Откройте образ (кликните на имя)
2. Справа вверху: **Package settings**
3. Пролистайте вниз до **"Danger Zone"**
4. Нажмите **"Change visibility"**
5. Выберите **"Public"**
6. Введите имя образа для подтверждения
7. Нажмите **"I understand, change package visibility"**

✅ Около имени package должен появиться badge **"Public"**

### 3.4 (Опционально) Настройте Workflow permissions

Если еще не настроено:

```
Settings → Actions → General → Workflow permissions
```

Выберите:
- 🔘 **Read and write permissions**
- ☑ **Allow GitHub Actions to create and approve pull requests**

Нажмите **Save**

---

## ✅ Этап 4: Проверка доступа к образам

### 4.1 Попробуйте скачать образы (без авторизации!)

```powershell
# Bot
docker pull ghcr.io/stril/systech-aidd-bot:latest

# API
docker pull ghcr.io/stril/systech-aidd-api:latest

# Frontend  
docker pull ghcr.io/stril/systech-aidd-frontend:latest
```

**Ожидаемый результат:**
```
latest: Pulling from stril/systech-aidd-bot
Status: Downloaded newer image for ghcr.io/stril/systech-aidd-bot:latest
```

✅ Образы скачались без ошибок "denied"

### 4.2 Проверьте загруженные образы

```powershell
docker images | Select-String "systech-aidd"
```

**Ожидаемый результат:**
```
ghcr.io/stril/systech-aidd-bot       latest   xxx   X minutes ago   XXX MB
ghcr.io/stril/systech-aidd-api       latest   xxx   X minutes ago   XXX MB
ghcr.io/stril/systech-aidd-frontend  latest   xxx   X minutes ago   XXX MB
```

---

## ✅ Этап 5: Запуск через docker-compose с registry образами

### 5.1 Остановите локальные контейнеры

```powershell
docker-compose down
```

### 5.2 Отредактируйте docker-compose.registry.yml

Замените `<owner>` на `stril`:

```powershell
(Get-Content docker-compose.registry.yml) -replace '<owner>', 'stril' | Set-Content docker-compose.registry.yml
```

### 5.3 Pull образов через docker-compose

```powershell
docker-compose -f docker-compose.registry.yml pull
```

**Ожидаемый результат:**
```
[+] Pulling 3/3
 ✔ api Pulled
 ✔ bot Pulled  
 ✔ frontend Pulled
```

### 5.4 Запустите контейнеры

```powershell
docker-compose -f docker-compose.registry.yml up -d
```

### 5.5 Проверьте статус

```powershell
docker-compose -f docker-compose.registry.yml ps
```

**Ожидаемый результат:**
```
NAME              STATUS         PORTS
aidd-api          Up             0.0.0.0:8000->8000/tcp
aidd-bot          Up
aidd-frontend     Up             0.0.0.0:3000->3000/tcp
```

### 5.6 Проверьте работу сервисов

```powershell
# API Health check
Invoke-WebRequest http://localhost:8000/health

# Frontend
Invoke-WebRequest http://localhost:3000

# Откройте в браузере
start http://localhost:8000/docs
start http://localhost:3000
```

**Ожидаемый результат:**
- ✅ API отвечает и показывает документацию
- ✅ Frontend загружается
- ✅ Все работает так же как с локальной сборкой

---

## ✅ Этап 6: Обновление документации и финализация

### 6.1 Обновите devops-roadmap.md

В файле `devops/doc/devops-roadmap.md` измените:

```markdown
| **D-SP-2** | Build & Publish | 🔄 В работе | ...
```

на:

```markdown
| **D-SP-2** | Build & Publish | ✅ Завершено | ...
```

### 6.2 Закоммитьте изменение

```bash
git checkout main
git pull origin main
# Отредактируйте devops-roadmap.md
git add devops/doc/devops-roadmap.md docker-compose.registry.yml
git commit -m "docs: mark D-SP-2 as completed and update registry config"
git push origin main
```

### 6.3 (Опционально) Обновите badge URL в README.md

Если нужно, замените username в badge:

```markdown
![Build Status](https://github.com/stril/systech-aidd/actions/workflows/build.yml/badge.svg)
```

---

## ✅ Этап 7: Финальная проверка

### 7.1 Чеклист завершения спринта

- [ ] Все 3 образа собираются успешно в CI
- [ ] Образы опубликованы в ghcr.io
- [ ] Образы публичные (доступны без авторизации)
- [ ] Образы можно скачать локально
- [ ] docker-compose.registry.yml работает
- [ ] Сервисы запускаются из registry образов
- [ ] API и Frontend работают корректно
- [ ] Документация обновлена
- [ ] Roadmap обновлен (статус ✅ Завершено)

### 7.2 Проверьте что готово к следующим спринтам

**D-SP-3: Manual Deploy**
- ✅ Образы в ghcr.io
- ✅ docker-compose.registry.yml готов
- ✅ Образы публичные (не требуют docker login на сервере)
- ✅ Автоматические миграции в образах
- ✅ Health checks настроены

**D-SP-4: Auto Deploy**
- ✅ CI/CD база создана
- ✅ Workflow работает
- ✅ Понимание GitHub Actions

---

## 📊 Метрики спринта

**Затраченное время:** ~4-6 часов (включая отладку)

**Созданные файлы:**
- ✅ `.github/workflows/build.yml`
- ✅ 4 файла документации (~2000 строк)
- ✅ `docker-compose.registry.yml`
- ✅ `docker-compose.override.yml.example`
- ✅ Обновлен README.md, roadmap

**Исправленные проблемы:**
1. ✅ Пути к Dockerfile
2. ✅ Lowercase имена registry
3. ✅ GitHub Actions cache
4. ✅ ENV переменные для Next.js
5. ✅ Отключение линтера
6. ✅ Отсутствующий formatters.ts (главная проблема!)

**Коммитов:** ~15

**Извлеченные уроки:**
- Всегда проверяйте .gitignore при "работает локально, падает в CI"
- Детальное логирование помогает найти проблему
- Анализ логов из GitHub Actions критически важен

---

## 🎉 Поздравляем!

Спринт D-SP-2 завершен! Теперь у вас есть:
- ✅ Автоматическая сборка образов при push в main
- ✅ Публикация в GitHub Container Registry
- ✅ Публичный доступ к образам
- ✅ Готовность к развертыванию (D-SP-3, D-SP-4)

**Следующий спринт:** D-SP-3 - Manual Deploy на сервер

---

**Дата завершения:** _____________  
**Подпись:** _____________

