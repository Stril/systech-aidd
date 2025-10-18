# Настройка GitHub Container Registry (ghcr.io)

## Введение

GitHub Container Registry (ghcr.io) - это бесплатный Docker registry от GitHub для хранения контейнерных образов. В этом руководстве описана пошаговая настройка для автоматической публикации образов.

## Предварительные требования

- ✅ Репозиторий на GitHub
- ✅ Workflow файл `.github/workflows/build.yml` создан
- ✅ Dockerfile'ы для сборки образов

## Шаг 1: Настройка прав доступа для GitHub Actions

GitHub Actions нужны права для публикации образов в Container Registry.

### 1.1. Перейдите в настройки репозитория

```
GitHub → Ваш репозиторий → Settings
```

### 1.2. Настройте Workflow permissions

```
Settings → Actions → General → Workflow permissions
```

Выберите одну из опций:

#### Вариант A: Read and write permissions (рекомендуется для начала)

```
⚪ Read repository contents and packages permissions
🔘 Read and write permissions
   ☑ Allow GitHub Actions to create and approve pull requests
```

**Преимущества:**
- ✅ Простая настройка
- ✅ Workflow может публиковать образы без дополнительных токенов
- ✅ Подходит для MVP и небольших проектов

**Недостатки:**
- ⚠️ Более широкие права для workflow

#### Вариант B: Read permissions + явные permissions в workflow (более безопасно)

```
🔘 Read repository contents and packages permissions
   ☐ Allow GitHub Actions to create and approve pull requests
```

И в workflow явно указать:

```yaml
jobs:
  build:
    permissions:
      contents: read
      packages: write
```

**Преимущества:**
- ✅ Минимальные права по умолчанию
- ✅ Явный контроль в каждом workflow
- ✅ Лучше для production и больших команд

### 1.3. Сохраните изменения

Нажмите **"Save"** внизу страницы.

## Шаг 2: Первый запуск workflow

После настройки прав нужно запустить workflow для создания первых образов.

### 2.1. Убедитесь что workflow файл в main

```bash
# Проверьте что .github/workflows/build.yml есть в main
git checkout main
git pull origin main
ls .github/workflows/build.yml
```

Если файла нет - смержите PR с workflow.

### 2.2. Запустите workflow вручную

```
GitHub → Actions → Build and Publish Docker Images → Run workflow
```

Или сделайте коммит в main:

```bash
git checkout main
git commit --allow-empty -m "ci: trigger initial build"
git push origin main
```

### 2.3. Дождитесь завершения

Перейдите в **Actions** tab и дождитесь зеленого статуса ✅.

**Что происходит:**
1. ✅ Собираются 3 образа (bot, api, frontend)
2. ✅ Образы тегируются как `latest` и `sha-<commit>`
3. ✅ Образы публикуются в GitHub Packages

## Шаг 3: Сделать образы публичными

После первой публикации образы по умолчанию **приватные** - нужно сделать их публичными для доступа без авторизации.

### 3.1. Перейдите в GitHub Packages

```
https://github.com/YOUR_USERNAME?tab=packages
```

Или через главную страницу GitHub → Your profile → Packages.

### 3.2. Найдите опубликованные образы

Вы должны увидеть 3 package:
- `systech-aidd-1-bot`
- `systech-aidd-1-api`
- `systech-aidd-1-frontend`

### 3.3. Измените visibility для каждого образа

**Для bot:**
1. Откройте `systech-aidd-1-bot`
2. **Package settings** (справа вверху)
3. Пролистайте вниз до **"Danger Zone"**
4. **Change visibility** → **Change visibility**
5. Выберите **"Public"**
6. Подтвердите изменение

**Повторите для api и frontend.**

### 3.4. Проверьте статус

После изменения около имени package должен появиться badge **"Public"**.

## Шаг 4: Проверка публичного доступа

Теперь проверим что образы доступны без авторизации.

### 4.1. Без docker login (анонимный pull)

```bash
# Замените YOUR_USERNAME на ваш GitHub username
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-api:latest
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-frontend:latest
```

**Ожидаемый результат:**
```
latest: Pulling from YOUR_USERNAME/systech-aidd-1-bot
...
Status: Downloaded newer image for ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
```

### 4.2. Запуск через docker-compose

```bash
# 1. Отредактируйте docker-compose.registry.yml
# Замените <owner> на YOUR_USERNAME

# 2. Pull образов
docker-compose -f docker-compose.registry.yml pull

# 3. Запуск
docker-compose -f docker-compose.registry.yml up -d

# 4. Проверка
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000
```

**Ожидаемый результат:**
- ✅ Все образы загружены
- ✅ Контейнеры запущены
- ✅ API и Frontend работают

## Шаг 5: Связать Package с репозиторием (опционально)

Это улучшит видимость packages в вашем репозитории.

### 5.1. Для каждого package:

1. Откройте Package settings
2. **Connect repository**
3. Выберите `systech-aidd-1`
4. **Connect**

### 5.2. Результат

В репозитории появится секция **"Packages"** справа с ссылками на образы.

## Использование образов

### Публичные образы (после Step 3)

```bash
# Pull latest версии
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest

# Pull конкретного commit
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:sha-abc1234

# Использование в docker-compose.registry.yml
docker-compose -f docker-compose.registry.yml up -d
```

**Авторизация НЕ требуется** ✅

### Приватные образы (если не сделали public)

```bash
# 1. Создать Personal Access Token (PAT)
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# Scopes: read:packages, write:packages

# 2. Сохранить токен в переменную
export CR_PAT=YOUR_TOKEN_HERE

# 3. Login в ghcr.io
echo $CR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 4. Теперь можно pull приватные образы
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
```

## Автоматическая публикация при push в main

После настройки workflow автоматически публикует образы:

```
git push origin main
  ↓
GitHub Actions запускает workflow
  ↓
Собирает 3 образа (bot, api, frontend)
  ↓
Публикует в ghcr.io с тегами:
  - latest
  - sha-<commit-hash>
```

### Просмотр статуса сборки

```
GitHub → Actions → Build and Publish Docker Images
```

Или добавьте badge в README:

```markdown
![Build Status](https://github.com/YOUR_USERNAME/systech-aidd-1/actions/workflows/build.yml/badge.svg)
```

## Troubleshooting

### Проблема: "Permission denied" при публикации

**Причина:** Недостаточно прав у GITHUB_TOKEN.

**Решение:**
1. Settings → Actions → General → Workflow permissions
2. Выберите "Read and write permissions"
3. Перезапустите workflow

### Проблема: Образы не появляются в Packages

**Причина:** Workflow не запущен или упал.

**Решение:**
1. Проверьте Actions → последний run
2. Посмотрите логи job'а
3. Исправьте ошибки в workflow или Dockerfile
4. Перезапустите workflow

### Проблема: "denied: permission_denied" при pull публичного образа

**Причина:** Образ все еще приватный.

**Решение:**
1. Откройте Package settings
2. Проверьте что visibility = Public
3. Попробуйте pull снова

### Проблема: "Rate limit exceeded" при pull

**Причина:** GitHub имеет лимиты на анонимные pull.

**Решение:**
1. Для публичных образов лимит высокий (маловероятно)
2. Сделайте docker login для повышения лимита:
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
   ```

## Полезные команды

### Просмотр всех тегов образа

```bash
# Через GitHub UI
GitHub → Packages → systech-aidd-1-bot → Package versions

# Через API
curl -H "Accept: application/vnd.github+json" \
  https://api.github.com/users/YOUR_USERNAME/packages/container/systech-aidd-1-bot/versions
```

### Удаление старых версий образов

```bash
# Через GitHub UI
Package settings → Manage versions → Delete
```

Или настройте автоматическую очистку через [Package cleanup policy](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).

### Инспекция образа

```bash
# Посмотреть метаданные
docker inspect ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest

# Посмотреть layers
docker history ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest

# Посмотреть размер
docker images ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
```

## Best Practices

1. ✅ **Делайте образы публичными** для Open Source проектов
2. ✅ **Используйте multi-stage builds** для уменьшения размера
3. ✅ **Тегируйте стабильные версии** - `v1.0.0`, `v1.0`, `v1`, `latest`
4. ✅ **Не храните секреты в образах** - используйте env variables
5. ✅ **Регулярно обновляйте base images** для security fixes
6. ✅ **Удаляйте старые версии** для экономии места

## Полезные ссылки

- [GitHub Packages Documentation](https://docs.github.com/en/packages)
- [Working with Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Publishing Docker Images to GitHub Packages](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images#publishing-images-to-github-packages)

---

**Следующие шаги:**
- [Тестирование CI/CD](ci-testing-guide.md)
- [Работа с Pull Requests](pull-requests-workflow.md)

