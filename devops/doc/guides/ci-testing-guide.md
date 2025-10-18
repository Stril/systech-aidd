# Руководство по тестированию CI/CD

## Введение

Это руководство описывает процесс тестирования GitHub Actions workflow для сборки и публикации Docker образов в нашем проекте.

## Стратегия тестирования

```
┌─────────────────────┐
│ 1. Локальная        │  Проверка сборки образов на вашей машине
│    проверка         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Тестирование     │  Проверка workflow через Pull Request
│    workflow на PR   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Проверка         │  Запуск с registry образами
│    публикации       │
└─────────────────────┘
```

## Этап 1: Локальная проверка (перед push)

Перед отправкой изменений в GitHub убедитесь, что образы собираются локально.

### 1.1. Проверка сборки всех образов

```bash
# Сборка всех образов через docker-compose
docker-compose build

# Или отдельно для каждого
docker build -f Dockerfile.bot -t systech-aidd-1-bot:test .
docker build -f Dockerfile.api -t systech-aidd-1-api:test .
docker build -f Dockerfile.frontend -t systech-aidd-1-frontend:test ./frontend
```

**Ожидаемый результат:**
```
✅ [+] Building 45.2s (12/12) FINISHED
✅ => => writing image sha256:...
```

**Если ошибки:**
- Проверьте Dockerfile синтаксис
- Убедитесь что все файлы существуют (COPY команды)
- Проверьте .dockerignore

### 1.2. Запуск собранных образов

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Проверка логов
docker-compose logs -f
```

**Ожидаемый результат:**
```
NAME              STATUS         PORTS
aidd-api          Up             0.0.0.0:8000->8000/tcp
aidd-bot          Up
aidd-frontend     Up             0.0.0.0:3000->3000/tcp
```

### 1.3. Функциональная проверка

```bash
# API Health check
curl http://localhost:8000/health
# Ожидается: {"status": "healthy"} или подобное

# Frontend
curl http://localhost:3000
# Ожидается: HTML страница

# API Documentation
open http://localhost:8000/docs  # macOS
start http://localhost:8000/docs # Windows
xdg-open http://localhost:8000/docs # Linux
```

### 1.4. Очистка

```bash
# Остановка сервисов
docker-compose down

# Очистка образов (опционально)
docker-compose down --rmi local

# Полная очистка (volumes + images)
docker-compose down -v --rmi all
```

### Чеклист локальной проверки

- [ ] `docker-compose build` успешно завершился
- [ ] Все 3 образа собраны (bot, api, frontend)
- [ ] `docker-compose up -d` запустил контейнеры
- [ ] `docker-compose ps` показывает все сервисы "Up"
- [ ] API отвечает на `/health`
- [ ] Frontend доступен на порту 3000
- [ ] Логи не показывают критичных ошибок

## Этап 2: Тестирование workflow через Pull Request

Workflow автоматически запускается при создании PR, но образы **не публикуются** в registry (только build для проверки).

### 2.1. Создание тестовой ветки

```bash
# Если вы уже в feature ветке - пропустите этот шаг
# Если работаете в main - создайте тестовую ветку

git checkout -b test/ci-workflow

# Сделайте тестовое изменение (например, в README)
echo "\n<!-- CI test -->" >> README.md
git add README.md
git commit -m "ci: test workflow"

# Push в GitHub
git push origin test/ci-workflow
```

### 2.2. Открытие Pull Request

1. Перейдите в GitHub репозиторий
2. Должна появиться кнопка **"Compare & pull request"**
3. Или: **Pull requests** → **New pull request**
4. Base: `main`, Compare: `test/ci-workflow`
5. Заполните описание PR
6. **Create pull request**

### 2.3. Мониторинг выполнения workflow

#### Через PR UI:

В PR найдите секцию **"Checks"** внизу:

```
⏳ Build and Publish Docker Images / build-and-push (bot)  In progress
⏳ Build and Publish Docker Images / build-and-push (api)  In progress
⏳ Build and Publish Docker Images / build-and-push (frontend)  In progress
```

Кликните **"Details"** для просмотра логов.

#### Через Actions tab:

```
GitHub → Actions → Build and Publish Docker Images → <ваш PR run>
```

### 2.4. Анализ результатов

**Успешный run:**
```
✅ build-and-push (bot)     2m 15s
✅ build-and-push (api)     2m 30s
✅ build-and-push (frontend) 3m 45s
```

**Что проверяется на PR:**
- ✅ Checkout code
- ✅ Setup Docker Buildx
- ✅ Build образов (без push в registry)
- ✅ Кэширование работает

**Что НЕ происходит на PR:**
- ❌ Login в ghcr.io (пропускается через `if: github.event_name != 'pull_request'`)
- ❌ Push образов в registry
- ❌ Публикация tags

### 2.5. Если workflow падает

**Шаг 1: Посмотрите логи**

В Actions откройте упавший job и найдите красную строку с ошибкой.

**Типичные ошибки:**

#### Ошибка: Docker build failed

```
ERROR [internal] load metadata for docker.io/library/python:3.11-slim
```

**Причина:** Проблемы с сетью или неверный base image.

**Решение:**
- Проверьте что base image существует
- Попробуйте пересобрать локально
- Перезапустите workflow (может быть временная проблема)

#### Ошибка: COPY failed - file not found

```
ERROR: failed to solve: failed to compute cache key: "/app/src" not found
```

**Причина:** Файл или директория не существует в context.

**Решение:**
- Проверьте что файл существует в репозитории
- Проверьте .dockerignore - не исключен ли файл
- Проверьте context в workflow (правильный ли путь)

#### Ошибка: Permission denied

```
ERROR: failed to solve: failed to create LLB definition: permission denied
```

**Причина:** Проблемы с правами или secrets.

**Решение:**
- Settings → Actions → Workflow permissions → "Read and write"

### 2.6. Исправление и повторная проверка

```bash
# 1. Исправьте код
# ... edit files ...

# 2. Коммит
git add .
git commit -m "fix: resolve Docker build error"

# 3. Push
git push origin test/ci-workflow

# 4. Workflow автоматически запустится снова
```

### Чеклист проверки на PR

- [ ] PR создан и workflow запущен
- [ ] Все 3 jobs (bot, api, frontend) зеленые ✅
- [ ] Логи не показывают warnings
- [ ] Build time разумный (< 5 минут с кэшем)
- [ ] В логах видно cache hits (ускорение сборки)

## Этап 3: Проверка публикации (после merge в main)

После merge PR в main workflow публикует образы в ghcr.io.

### 3.1. Merge PR

```
GitHub → Pull Request → Squash and merge
```

Или через командную строку:
```bash
git checkout main
git pull origin main
# Должны увидеть изменения из PR
```

### 3.2. Проверка workflow на main

```
GitHub → Actions → Build and Publish Docker Images → <latest run>
```

**Что происходит на main (отличия от PR):**
- ✅ Login в ghcr.io (step не пропускается)
- ✅ Push образов в registry
- ✅ Tags: `latest` + `sha-<commit-hash>`

### 3.3. Проверка публикации в GitHub Packages

```
GitHub → Packages (или https://github.com/YOUR_USERNAME?tab=packages)
```

Должны появиться 3 packages:
- `systech-aidd-1-bot`
- `systech-aidd-1-api`
- `systech-aidd-1-frontend`

**Проверьте:**
- [ ] Packages существуют
- [ ] Latest tag присутствует
- [ ] sha-xxx tag присутствует
- [ ] Visibility = Public (если настроили)

### 3.4. Pull образов из registry

```bash
# Замените YOUR_USERNAME на ваш GitHub username
export OWNER=YOUR_USERNAME

# Pull latest образов
docker pull ghcr.io/$OWNER/systech-aidd-1-bot:latest
docker pull ghcr.io/$OWNER/systech-aidd-1-api:latest
docker pull ghcr.io/$OWNER/systech-aidd-1-frontend:latest
```

**Ожидаемый результат:**
```
latest: Pulling from YOUR_USERNAME/systech-aidd-1-bot
abc123: Pull complete
def456: Pull complete
...
Status: Downloaded newer image for ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
```

**Если "denied: permission_denied":**
- Образы приватные - сделайте их публичными (см. [github-registry-setup.md](github-registry-setup.md))
- Или сделайте `docker login ghcr.io`

### 3.5. Запуск через docker-compose.registry.yml

```bash
# 1. Отредактируйте docker-compose.registry.yml
sed -i 's/<owner>/YOUR_USERNAME/g' docker-compose.registry.yml  # Linux/macOS
# Windows: вручную замените <owner> на YOUR_USERNAME

# 2. Pull всех образов
docker-compose -f docker-compose.registry.yml pull

# 3. Остановите локальные контейнеры (если запущены)
docker-compose down

# 4. Запуск с registry образами
docker-compose -f docker-compose.registry.yml up -d

# 5. Проверка
docker-compose -f docker-compose.registry.yml ps
```

**Ожидаемый результат:**
```
NAME              STATUS         PORTS
aidd-api          Up             0.0.0.0:8000->8000/tcp
aidd-bot          Up
aidd-frontend     Up             0.0.0.0:3000->3000/tcp
```

### 3.6. Функциональная проверка

```bash
# API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Dashboard (если доступен)
open http://localhost:3000/dashboard
```

### 3.7. Очистка после тестирования

```bash
# Остановка
docker-compose -f docker-compose.registry.yml down

# Возврат к локальной разработке
docker-compose up -d
```

### Чеклист проверки публикации

- [ ] Workflow на main успешно завершился
- [ ] 3 packages появились в GitHub Packages
- [ ] Образы имеют теги `latest` и `sha-xxx`
- [ ] Pull образов работает без ошибок
- [ ] `docker-compose.registry.yml` успешно запускает все сервисы
- [ ] API и Frontend работают корректно

## Этап 4: Регрессионное тестирование

Периодически проверяйте что CI работает стабильно.

### 4.1. Ручной запуск workflow

```
GitHub → Actions → Build and Publish Docker Images → Run workflow
  Branch: main
  → Run workflow
```

Это полезно для:
- Пересборки образов без кода изменений (например, после обновления base image)
- Проверки что CI еще работает
- Обновления `latest` tag

### 4.2. Мониторинг статуса сборки

Добавьте badge в README для видимости статуса:

```markdown
![Build Status](https://github.com/YOUR_USERNAME/systech-aidd-1/actions/workflows/build.yml/badge.svg)
```

### 4.3. Notifications о падении CI

**GitHub автоматически отправляет email** если ваш commit сломал CI.

**Настройка дополнительных уведомлений:**

Settings → Notifications → Actions → Выберите уведомления:
- ✅ Only notify for failed workflows
- ✅ Send notifications for workflow runs on my repositories

## Troubleshooting

### Проблема: Workflow не запускается на PR

**Причина:** Триггер не настроен или ветка не соответствует.

**Проверьте workflow:**
```yaml
on:
  pull_request:
    branches: [main]  # PR должен быть в main
```

**Решение:**
- Убедитесь что PR открыт в `main`
- Проверьте что workflow файл существует в base ветке

### Проблема: Кэширование не работает

**Симптомы:** Каждая сборка занимает полное время (> 5 минут).

**Проверьте логи:**
```
#8 importing cache manifest from ghcr.io/...
#8 ERROR: failed to solve: ghcr.io/...: not found
```

**Решение:**
- Первая сборка всегда долгая (кэш еще не создан)
- Последующие сборки должны использовать кэш
- Если не работает - проверьте что образы публичные

### Проблема: Registry образы старые

**Симптомы:** Pulled образ не содержит последние изменения.

**Причина:** Кэширование Docker локально или в registry.

**Решение:**
```bash
# Принудительно pull свежих образов
docker-compose -f docker-compose.registry.yml pull --no-cache

# Или удалите локальные образы
docker rmi ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
docker pull ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest
```

### Проблема: Логи workflow слишком большие

**Причина:** Verbose logging в Dockerfile build steps.

**Решение:**
- Минимизируйте лишний output в Dockerfile
- Используйте `--quiet` где возможно
- Группируйте RUN команды

## Автоматизация тестирования (будущее)

В следующих спринтах добавим:

```yaml
jobs:
  lint:
    - name: Run linter
      run: make lint
  
  test:
    - name: Run tests
      run: make test
  
  build:
    needs: [lint, test]  # Собирать только если lint и tests прошли
```

## Best Practices

1. ✅ **Тестируйте локально первым делом** - экономит время на CI
2. ✅ **Используйте PR для проверки** - не ломайте main
3. ✅ **Мониторьте время сборки** - оптимизируйте если > 5 минут
4. ✅ **Проверяйте размер образов** - используйте multi-stage builds
5. ✅ **Регулярно проверяйте registry** - удаляйте старые версии
6. ✅ **Настройте уведомления** - будьте в курсе о проблемах

## Полезные команды

### Просмотр размеров образов

```bash
docker images | grep systech-aidd-1
```

### Сравнение локального и registry образа

```bash
# Локальный
docker inspect systech-aidd-1-bot:latest | jq '.[0].Size'

# Registry
docker inspect ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:latest | jq '.[0].Size'
```

### Очистка старых образов

```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить конкретный образ
docker rmi ghcr.io/YOUR_USERNAME/systech-aidd-1-bot:sha-old123
```

## Полезные ссылки

- [GitHub Actions Debugging](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging)
- [Docker Build Troubleshooting](https://docs.docker.com/engine/reference/commandline/build/#troubleshooting)
- [Act - Run Actions Locally](https://github.com/nektos/act)

---

**Связанные документы:**
- [Введение в GitHub Actions](github-actions-intro.md)
- [Настройка GitHub Container Registry](github-registry-setup.md)
- [Работа с Pull Requests](pull-requests-workflow.md)

