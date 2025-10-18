# План реализации Спринта D-SP-2: Build & Publish

## Цель

Автоматическая сборка и публикация Docker образов (bot, api, frontend) в GitHub Container Registry при push в main, обеспечивая основу для будущих спринтов по развертыванию.

## Контекст

**Исходное состояние:**
- Есть 3 Dockerfile: `Dockerfile.bot`, `Dockerfile.api`, `frontend/Dockerfile.frontend`
- `docker-compose.yml` настроен для локальной сборки через `build:`
- Образы собираются и работают локально
- Отсутствует `.github/workflows/`

**Целевое состояние:**
- Образы автоматически собираются и публикуются в ghcr.io
- Поддержка 2 режимов работы: local build и registry images
- Публичный доступ к образам (без авторизации)
- Готовность к D-SP-3 (manual deploy) и D-SP-4 (auto deploy)

## Структура работ

### 1. Подготовка (первый шаг)

**Создание ветки для тестирования workflow:**

```bash
# 1. Создать feature ветку для разработки CI/CD
git checkout -b feature/d-sp-2-ci-cd

# 2. Все изменения будут делаться в этой ветке
# 3. После создания workflow можно будет протестировать через PR
```

**Цель этапа:**
- Изолировать работу над CI/CD от main ветки
- Возможность тестирования workflow через Pull Request
- Проверка сборки образов на PR перед merge в main

**Результат:**
- Создана ветка `feature/d-sp-2-ci-cd`
- Все дальнейшие изменения коммитятся в эту ветку

### 2. Документация по GitHub Actions (devops/doc/guides/)

**Файл: `devops/doc/guides/github-actions-intro.md`**

Создать русскоязычную инструкцию с разделами:
- Что такое GitHub Actions и workflow
- Структура `.github/workflows/*.yml`
- Триггеры событий (push, pull_request, workflow_dispatch, schedule)
- Основные концепции: jobs, steps, actions, matrix strategy
- Работа с Docker в Actions (build, push, login)
- GitHub Container Registry (ghcr.io) - публичные vs приватные образы
- Примеры базовых workflow

**Файл: `devops/doc/guides/pull-requests-workflow.md`**

Объяснить процесс работы с PR:
- Создание feature branch
- Открытие Pull Request
- Запуск CI checks на PR
- Code review процесс
- Merge в main и автоматическая сборка образов

### 3. GitHub Actions Workflow

**Файл: `.github/workflows/build.yml`**

Создать workflow со следующей структурой:

```yaml
name: Build and Publish Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ghcr.io/${{ github.repository_owner }}/systech-aidd-1

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    strategy:
      matrix:
        include:
          - service: bot
            dockerfile: Dockerfile.bot
            context: .
          - service: api
            dockerfile: Dockerfile.api
            context: .
          - service: frontend
            dockerfile: Dockerfile.frontend
            context: ./frontend

    steps:
      - checkout
      - Docker Buildx setup
      - Login to ghcr.io (только для push в main)
      - Extract metadata (tags, labels)
      - Build and push (кэширование layers)
```

**Ключевые особенности:**
- Matrix strategy для параллельной сборки 3 образов
- Кэширование Docker layers через `cache-from`/`cache-to`
- Тегирование: `latest` + `sha-<commit_sha>`
- Push только при push в main (не при PR)
- Использование `docker/build-push-action@v5`

### 4. Конфигурация docker-compose

**Файл: `docker-compose.override.yml.example`**

Создать пример override-файла для работы с registry образами:

```yaml
services:
  api:
    image: ghcr.io/<owner>/systech-aidd-1-api:latest
    build: ~  # Отключить локальную сборку

  bot:
    image: ghcr.io/<owner>/systech-aidd-1-bot:latest
    build: ~

  frontend:
    image: ghcr.io/<owner>/systech-aidd-1-frontend:latest
    build: ~
```

**Файл: `docker-compose.registry.yml`**

Создать альтернативную версию для явного использования registry:

```yaml
services:
  api:
    image: ghcr.io/<owner>/systech-aidd-1-api:latest
    # копия конфигурации из docker-compose.yml (volumes, ports, env)
```

**Обновить: `docker-compose.yml`**

Добавить комментарии о возможности переключения режимов:
```yaml
# Локальная сборка (по умолчанию):
#   docker-compose up --build
#
# Использование образов из registry:
#   docker-compose -f docker-compose.registry.yml up
```

### 5. Публичный доступ к образам

**Файл: `devops/doc/guides/github-registry-setup.md`**

Создать пошаговую инструкцию:

1. **Настройка прав доступа к packages:**
   - Settings → Actions → General → Workflow permissions
   - Выбрать "Read and write permissions"

2. **После первой публикации сделать образы публичными:**
   - Перейти в Package settings (github.com/users/<owner>/packages)
   - Для каждого образа (bot, api, frontend):
     - Package settings → Danger Zone → Change visibility
     - Выбрать "Public"

3. **Проверка публичного доступа:**
   ```bash
   docker pull ghcr.io/<owner>/systech-aidd-1-bot:latest
   # Должно работать без docker login
   ```

### 6. Тестирование и верификация

**Файл: `devops/doc/guides/ci-testing-guide.md`**

Создать инструкцию по тестированию CI:

**Локальное тестирование перед push:**
```bash
# 1. Проверка сборки всех образов
docker-compose build

# 2. Проверка запуска
docker-compose up -d
docker-compose ps
docker-compose logs

# 3. Очистка
docker-compose down
```

**Тестирование workflow в отдельной ветке:**
```bash
# 1. Создать ветку test/ci-workflow
git checkout -b test/ci-workflow

# 2. Push ветки запустит workflow на PR
git push origin test/ci-workflow

# 3. Открыть PR и проверить Actions tab
```

**Проверка работы с registry образами:**
```bash
# 1. Pull образов из registry
docker-compose -f docker-compose.registry.yml pull

# 2. Запуск
docker-compose -f docker-compose.registry.yml up -d

# 3. Проверка работоспособности
curl http://localhost:8000/health
curl http://localhost:3000
```

### 7. Обновление документации

**Обновить: `README.md`**

Добавить в начало файла badges:
```markdown
![Build Status](https://github.com/<owner>/systech-aidd-1/actions/workflows/build.yml/badge.svg)
```

Добавить новую секцию после "🐳 Быстрый старт через Docker":

```markdown
### Использование образов из GitHub Container Registry

Если вы не хотите собирать образы локально, можете использовать готовые:

\`\`\`bash
# Использование latest образов из registry
docker-compose -f docker-compose.registry.yml up -d

# Указание конкретной версии (commit SHA)
docker pull ghcr.io/<owner>/systech-aidd-1-bot:sha-abc1234
\`\`\`

Образы доступны публично и не требуют авторизации.
```

**Обновить: `devops/doc/devops-roadmap.md`**

Изменить статус D-SP-2 с "📋 Планируется" на "🔄 В работе", добавить ссылку на план:
```markdown
| **D-SP-2** | Build & Publish | 🔄 В работе | ... | ... | [План](plans/d-sp-2-implementation.md) |
```

**Создать: `devops/doc/plans/d-sp-2-implementation.md`**

Скопировать этот план реализации в отдельный файл для справки.

### 8. Структура файлов после выполнения

```
systech-aidd-1/
├── .github/
│   └── workflows/
│       └── build.yml                           # NEW: CI/CD workflow
├── devops/
│   └── doc/
│       ├── guides/
│       │   ├── github-actions-intro.md         # NEW: Введение в GitHub Actions
│       │   ├── pull-requests-workflow.md       # NEW: Работа с PR
│       │   ├── github-registry-setup.md        # NEW: Настройка ghcr.io
│       │   └── ci-testing-guide.md             # NEW: Тестирование CI
│       ├── plans/
│       │   └── d-sp-2-implementation.md        # NEW: Этот план
│       └── devops-roadmap.md                   # UPDATE: Статус спринта
├── docker-compose.yml                          # UPDATE: Комментарии о режимах
├── docker-compose.registry.yml                 # NEW: Registry-based compose
├── docker-compose.override.yml.example         # NEW: Пример override
└── README.md                                   # UPDATE: Badges + секция registry
```

## Критерии приёмки

- ✅ Workflow `.github/workflows/build.yml` создан и работает
- ✅ При push в main автоматически собираются 3 образа
- ✅ Образы публикуются в ghcr.io с тегами latest и sha-<commit>
- ✅ Образы публичные и доступны без авторизации
- ✅ Создана полная документация по GitHub Actions и PR
- ✅ Есть 2 способа запуска: локальная сборка и registry images
- ✅ README обновлен с badges и инструкциями
- ✅ Локально проверен pull и запуск образов из registry
- ✅ CI проверен на тестовой ветке через PR

## MVP ограничения (не делаем сейчас)

- ❌ Lint checks в CI (будет в следующих спринтах)
- ❌ Тесты в CI (будет в следующих спринтах)
- ❌ Security scanning (будет позже)
- ❌ Multi-platform builds (amd64/arm64) (будет позже)
- ❌ Автоматический деплой (это D-SP-4)

## Статус выполнения

**Дата начала:** 18 октября 2025

**Выполненные задачи:**
- ✅ Создана ветка `feature/d-sp-2-ci-cd`
- ✅ Создан файл `.github/workflows/build.yml`
- ✅ Создана документация по GitHub Actions (4 файла)
- ✅ Созданы docker-compose файлы для registry режима
- ✅ Обновлен README.md с badge и секцией registry
- ✅ Обновлен devops-roadmap.md статус спринта
- ✅ Создан план реализации

**Следующие шаги:**
1. Коммит и push изменений в feature ветку
2. Открыть Pull Request для тестирования workflow
3. После успешной проверки - merge в main
4. Настроить публичный доступ к образам в GitHub Packages
5. Проверить работу с registry образами

---

**Автор:** AI Assistant (Cursor)
**Дата создания:** 18 октября 2025

