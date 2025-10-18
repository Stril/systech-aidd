# Введение в GitHub Actions

## Что такое GitHub Actions?

**GitHub Actions** — это встроенная в GitHub платформа CI/CD (Continuous Integration / Continuous Deployment), которая позволяет автоматизировать процессы разработки, тестирования и развертывания прямо в вашем репозитории.

### Основные преимущества:

- ✅ **Встроенность** - работает прямо в GitHub, не нужны сторонние сервисы
- ✅ **Бесплатность** - 2000 минут/месяц для приватных репозиториев, неограниченно для публичных
- ✅ **Гибкость** - мощная система триггеров и условий
- ✅ **Переиспользование** - огромная экосистема готовых Actions
- ✅ **Интеграция** - полная интеграция с Pull Requests, Issues, Releases

## Структура Workflow

Workflow хранятся в директории `.github/workflows/` в формате YAML.

### Базовая структура:

```yaml
name: Название workflow                # Отображается в GitHub UI

on:                                     # Триггеры запуска
  push:
    branches: [main]

jobs:                                   # Задачи для выполнения
  job-name:                            # Имя задачи
    runs-on: ubuntu-latest             # Операционная система
    steps:                             # Шаги выполнения
      - name: Checkout code
        uses: actions/checkout@v4      # Использование готового action

      - name: Run command
        run: echo "Hello World"        # Выполнение команды
```

### Ключевые компоненты:

1. **Workflow** - файл `.yml` с описанием автоматизации
2. **Jobs** - группы шагов, которые выполняются на одном runner
3. **Steps** - отдельные команды или actions
4. **Actions** - переиспользуемые блоки кода (свои или из Marketplace)
5. **Runners** - виртуальные машины, где выполняется код

## Триггеры событий (Events)

### Push и Pull Request

Самые популярные триггеры:

```yaml
on:
  push:
    branches: [main, develop]          # При push в main или develop
    paths:
      - 'src/**'                        # Только если изменились файлы в src/

  pull_request:
    branches: [main]                    # При создании PR в main
    types: [opened, synchronize]        # При открытии или обновлении PR
```

### Manual dispatch (ручной запуск)

```yaml
on:
  workflow_dispatch:                    # Кнопка в GitHub UI для ручного запуска
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

### Schedule (по расписанию)

```yaml
on:
  schedule:
    - cron: '0 0 * * *'                # Каждый день в полночь (UTC)
    - cron: '0 */6 * * *'              # Каждые 6 часов
```

### Другие события

- `release` - при создании release
- `issues` - при работе с issues
- `workflow_call` - для переиспользования workflow
- `repository_dispatch` - для внешних триггеров через API

## Основные концепции

### Jobs и параллельность

По умолчанию jobs выполняются **параллельно**:

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
```

Для последовательного выполнения используйте `needs`:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

  deploy:
    runs-on: ubuntu-latest
    needs: build                        # Запустится только после успешного build
    steps:
      - run: npm run deploy
```

### Matrix Strategy (матричная стратегия)

Позволяет запустить job с разными параметрами параллельно:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]      # Запустится 3 раза
        os: [ubuntu-latest, windows-latest]  # × 2 ОС = 6 jobs
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
```

**Для нашего проекта** используем matrix для сборки 3 Docker образов:

```yaml
strategy:
  matrix:
    include:
      - service: bot
        dockerfile: Dockerfile.bot
      - service: api
        dockerfile: Dockerfile.api
      - service: frontend
        dockerfile: Dockerfile.frontend
```

### Secrets и Environment Variables

**Секреты** хранятся в Settings → Secrets and variables → Actions:

```yaml
steps:
  - name: Login to Docker Hub
    run: echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
```

**Переменные окружения**:

```yaml
env:
  REGISTRY: ghcr.io
  NODE_VERSION: 18

jobs:
  build:
    env:
      BUILD_ENV: production             # Для конкретного job
    steps:
      - run: echo $REGISTRY             # Доступна глобальная переменная
      - run: echo $BUILD_ENV            # Доступна переменная job
```

## Работа с Docker в Actions

### Базовый пример сборки образа:

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:latest .

      - name: Run tests in container
        run: docker run myapp:latest npm test
```

### Использование Docker Actions (рекомендуется):

GitHub предоставляет официальные actions для работы с Docker:

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3  # Расширенные возможности сборки

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}  # Автоматически доступен

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache
          cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache,mode=max
```

### Кэширование Docker layers

Кэширование значительно ускоряет сборку:

```yaml
- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    cache-from: type=registry,ref=ghcr.io/user/repo:buildcache
    cache-to: type=registry,ref=ghcr.io/user/repo:buildcache,mode=max
```

**Типы кэширования:**
- `type=registry` - сохраняет кэш в registry (рекомендуется)
- `type=local` - локальный кэш на runner
- `type=gha` - GitHub Actions cache

## GitHub Container Registry (ghcr.io)

### Что такое ghcr.io?

**GitHub Container Registry** - бесплатный Docker registry от GitHub для хранения контейнерных образов.

### Преимущества:

- ✅ **Бесплатный** для публичных репозиториев
- ✅ **Интеграция** с GitHub Actions и Packages
- ✅ **Анонимный pull** для публичных образов
- ✅ **Автоматическая аутентификация** через `GITHUB_TOKEN`

### Публичные vs Приватные образы

#### Публичные образы (Public):
- Доступны всем без авторизации
- `docker pull ghcr.io/username/repo:latest` работает сразу
- Рекомендуется для Open Source проектов

#### Приватные образы (Private):
- Требуют аутентификации для pull
- Нужен `docker login ghcr.io` с Personal Access Token
- По умолчанию все новые образы приватные

### Как сделать образ публичным:

1. Перейти на `https://github.com/users/USERNAME/packages`
2. Выбрать нужный package
3. **Package settings** → **Danger Zone** → **Change visibility**
4. Выбрать **Public**

### Формат имен образов:

```
ghcr.io/OWNER/IMAGE_NAME:TAG
```

Примеры:
- `ghcr.io/microsoft/vscode:latest`
- `ghcr.io/myuser/myapp:v1.0.0`
- `ghcr.io/myorg/systech-aidd-1-bot:sha-abc1234`

## Примеры базовых workflow

### Пример 1: Запуск тестов при PR

```yaml
name: Tests

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run tests
        run: make test
```

### Пример 2: Деплой по ручному запуску

```yaml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to ${{ inputs.environment }}
        run: ./deploy.sh ${{ inputs.environment }}
```

### Пример 3: Сборка и публикация Docker образа

```yaml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

## Permissions (права доступа)

GitHub Actions использует токен `GITHUB_TOKEN` с ограниченными правами.

### Настройка прав в workflow:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read        # Чтение кода
      packages: write       # Публикация в GitHub Packages
      issues: write         # Комментарии в issues
```

### Глобальная настройка прав:

**Settings** → **Actions** → **General** → **Workflow permissions**:
- **Read repository contents permission** (безопаснее, по умолчанию)
- **Read and write permissions** (нужно для публикации образов)

## Отладка и мониторинг

### Просмотр логов:

1. Откройте **Actions** tab в GitHub
2. Выберите нужный workflow run
3. Кликните на job, чтобы увидеть логи

### Debug логирование:

Добавьте секреты для детальных логов:
- `ACTIONS_RUNNER_DEBUG` = `true`
- `ACTIONS_STEP_DEBUG` = `true`

### Локальная отладка:

Используйте [act](https://github.com/nektos/act) для запуска Actions локально:

```bash
# Установка
brew install act  # macOS
choco install act # Windows

# Запуск workflow локально
act push
act pull_request
```

## Best Practices

1. ✅ **Используйте версии actions** - `actions/checkout@v4`, не `@main`
2. ✅ **Кэшируйте зависимости** - ускоряет выполнение в 2-3 раза
3. ✅ **Matrix для параллелизма** - тестируйте на разных версиях
4. ✅ **Fail fast** - `fail-fast: true` останавливает все jobs при первой ошибке
5. ✅ **Минимальные permissions** - указывайте только необходимые права
6. ✅ **Секреты для чувствительных данных** - никогда не hardcode токены
7. ✅ **Условия для оптимизации** - `if: github.event_name == 'push'`

## Полезные ссылки

- [Официальная документация GitHub Actions](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Awesome Actions - коллекция примеров](https://github.com/sdras/awesome-actions)
- [Docker Actions](https://github.com/docker/build-push-action)

---

**Следующие шаги:**
- [Работа с Pull Requests](pull-requests-workflow.md)
- [Настройка GitHub Container Registry](github-registry-setup.md)
- [Тестирование CI/CD](ci-testing-guide.md)

