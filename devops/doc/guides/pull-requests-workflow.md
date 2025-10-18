# Работа с Pull Requests и CI/CD

## Введение

Pull Request (PR) - основной механизм code review и интеграции изменений в проекте. В комбинации с GitHub Actions это мощный инструмент для обеспечения качества кода.

## Workflow: От feature branch до production

```
┌─────────────────┐
│ 1. Feature      │
│    Branch       │  git checkout -b feature/new-feature
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Commits      │  git commit -m "feat: ..."
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Push         │  git push origin feature/new-feature
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Open PR      │  GitHub UI: New Pull Request
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. CI Checks    │  GitHub Actions автоматически запускаются
│    Run          │  - Build образов
│                 │  - Lint (будущее)
│                 │  - Tests (будущее)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Code Review  │  Reviewer проверяет код
│                 │  - Комментарии
│                 │  - Request changes / Approve
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. Merge to     │  Merge pull request (Squash and merge)
│    main         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 8. Deploy       │  GitHub Actions собирает и публикует образы
│    Trigger      │  в ghcr.io (только для main)
└─────────────────┘
```

## 1. Создание Feature Branch

### Именование веток

Используйте префиксы для типа изменений:

- `feature/` - новая функциональность
- `fix/` - исправление бага
- `refactor/` - рефакторинг без изменения функциональности
- `docs/` - изменения в документации
- `test/` - добавление или обновление тестов
- `chore/` - обновление зависимостей, конфигурации

**Примеры:**
```bash
git checkout -b feature/add-user-auth
git checkout -b fix/database-connection-leak
git checkout -b docs/update-readme
git checkout -b test/add-integration-tests
git checkout -b refactor/extract-service-layer
```

### Создание ветки

```bash
# 1. Убедитесь, что main актуален
git checkout main
git pull origin main

# 2. Создайте новую ветку
git checkout -b feature/my-feature

# 3. Внесите изменения
# ... редактируйте файлы ...

# 4. Коммит изменений
git add .
git commit -m "feat: add new feature"

# 5. Push в remote
git push origin feature/my-feature
```

## 2. Коммиты и Conventional Commits

### Формат коммитов

Используйте [Conventional Commits](https://www.conventionalcommits.org/) для читаемости истории:

```
<type>: <description>

[optional body]

[optional footer]
```

### Типы коммитов:

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование, запятые, пробелы (не влияет на код)
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, build процесса
- `perf:` - улучшение производительности
- `ci:` - изменения в CI/CD

**Примеры хороших коммитов:**
```bash
git commit -m "feat: add user authentication via JWT"
git commit -m "fix: resolve database connection pool leak"
git commit -m "docs: update API documentation for /users endpoint"
git commit -m "refactor: extract database logic to separate service"
git commit -m "test: add unit tests for UserService"
git commit -m "ci: add Docker build workflow"
```

**Плохие примеры:**
```bash
git commit -m "update"           # ❌ Не понятно что изменено
git commit -m "fix stuff"        # ❌ Слишком общее
git commit -m "WIP"              # ❌ Work In Progress - не коммитьте незавершенное
```

## 3. Открытие Pull Request

### Через GitHub UI

1. После push GitHub покажет кнопку **"Compare & pull request"**
2. Или перейдите в **Pull Requests** → **New pull request**
3. Выберите ветки:
   - **base:** `main` (куда мержим)
   - **compare:** `feature/my-feature` (что мержим)

### Заполнение PR

**Хороший PR включает:**

```markdown
## Описание

Краткое описание что делает этот PR.

## Изменения

- Добавлена функция X
- Исправлен баг Y
- Обновлена документация Z

## Тестирование

- [ ] Локально протестировано через `docker-compose up`
- [ ] Добавлены unit тесты
- [ ] CI checks проходят

## Screenshots (если UI изменения)

![image](url)

## Связанные задачи

Closes #123
```

### Черновик PR (Draft)

Для незавершенной работы создавайте Draft PR:

```
GitHub UI → New Pull Request → Create Draft Pull Request
```

**Преимущества Draft:**
- CI checks все равно запускаются
- Показывает прогресс работы команде
- Можно получить ранний фидбек
- Нельзя случайно смержить

**Когда готово:**
```
Ready for review → Convert to ready for review
```

## 4. CI Checks на Pull Request

### Автоматический запуск

При открытии или обновлении PR автоматически запускаются все workflow с триггером `pull_request`:

```yaml
on:
  pull_request:
    branches: [main]
```

### Что проверяется в нашем проекте (D-SP-2)

**Текущий этап (D-SP-2):**
- ✅ Сборка Docker образов (bot, api, frontend)
- ⏸️ Образы **не публикуются** в ghcr.io (только build для проверки)

**Будущие этапы:**
- 🔜 Lint checks (ruff, mypy)
- 🔜 Unit tests (pytest)
- 🔜 Integration tests
- 🔜 Security scanning

### Просмотр результатов CI

1. В PR найдите секцию **"Checks"**
2. Кликните на **"Details"** для просмотра логов
3. Все checks должны быть зелеными ✅ перед merge

### Если CI падает:

```bash
# 1. Посмотрите логи в GitHub Actions
# 2. Воспроизведите локально
docker-compose build

# 3. Исправьте ошибку
# ... edit files ...

# 4. Коммит и push
git add .
git commit -m "fix: resolve Docker build error"
git push origin feature/my-feature

# 5. CI автоматически запустится снова
```

## 5. Code Review процесс

### Для автора PR:

1. ✅ **Самопроверка** - прочитайте свой diff перед отправкой
2. ✅ **Описание** - объясните зачем и что сделано
3. ✅ **Размер** - держите PR маленькими (< 500 строк идеально)
4. ✅ **Тесты** - добавьте тесты для новой функциональности
5. ✅ **CI зеленый** - все checks проходят

### Для reviewer:

1. **Понимание** - убедитесь что понимаете зачем нужны изменения
2. **Логика** - проверьте корректность реализации
3. **Стиль** - соответствие coding standards проекта
4. **Тесты** - есть ли покрытие тестами
5. **Security** - нет ли уязвимостей

### Типы комментариев:

**Blocking (требует исправления):**
```
❌ Request changes: Этот код создает SQL injection уязвимость
```

**Non-blocking (предложение):**
```
💡 Comment: Можно упростить этот код через list comprehension
```

**Approval:**
```
✅ Approve: LGTM (Looks Good To Me)
```

### Ответ на комментарии:

```bash
# 1. Исправьте код согласно фидбеку
# 2. Commit и push
git add .
git commit -m "fix: address review comments"
git push origin feature/my-feature

# 3. Ответьте на комментарии в GitHub
# 4. Нажмите "Resolve conversation" когда исправлено
```

## 6. Merge в main

### Стратегии merge

GitHub предлагает 3 стратегии:

#### 1. Merge commit (по умолчанию)
```
   A---B---C feature
  /         \
-D-----------M main
```
- Сохраняет всю историю коммитов
- Создает merge commit
- История может быть сложной

#### 2. Squash and merge ⭐ (рекомендуется)
```
   A---B---C feature
  /
-D-----S main
```
- Объединяет все коммиты в один
- Чистая линейная история
- Легко откатить изменения

#### 3. Rebase and merge
```
   A---B---C feature
  /
-D-A'-B'-C' main
```
- Переписывает историю
- Линейная история без merge commits

### Для нашего проекта: Squash and merge

**Почему:**
- 🎯 Чистая история в main
- 🎯 Один коммит = один PR = одна фича/фикс
- 🎯 Легко откатить через `git revert`

**Как:**
1. После approve кликните **"Squash and merge"**
2. Отредактируйте commit message (если нужно)
3. Confirm merge
4. **Delete branch** после merge (рекомендуется)

### После merge в main

**Автоматически происходит:**

1. ✅ GitHub Actions запускает workflow для `main`
2. ✅ Собираются Docker образы
3. ✅ Образы публикуются в ghcr.io с тегами:
   - `latest`
   - `sha-<commit-hash>`

## 7. Protected Branches (настройка main)

### Рекомендуемые правила для main:

**Settings** → **Branches** → **Branch protection rules** → **Add rule**:

```
Branch name pattern: main

☑ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Dismiss stale pull request approvals when new commits are pushed

☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
  ☑ Status checks: [выбрать build job из Actions]

☑ Require conversation resolution before merging

☐ Require signed commits (опционально)

☐ Require linear history (если используете squash, не обязательно)

☑ Do not allow bypassing the above settings (для админов тоже)
```

**Что это дает:**
- ✅ Нельзя push напрямую в main
- ✅ Все изменения только через PR
- ✅ CI должен пройти перед merge
- ✅ Требуется code review

## Практические примеры

### Пример 1: Добавление новой фичи

```bash
# 1. Создать ветку
git checkout -b feature/add-telegram-commands

# 2. Внести изменения
# ... code ...

# 3. Коммиты
git add .
git commit -m "feat: add /stats command"
git commit -m "test: add tests for stats command"

# 4. Push
git push origin feature/add-telegram-commands

# 5. Открыть PR в GitHub UI
# 6. Дождаться CI и code review
# 7. Squash and merge
```

### Пример 2: Исправление бага

```bash
# 1. Создать ветку
git checkout -b fix/database-connection-leak

# 2. Исправить баг
# ... fix code ...

# 3. Коммит
git commit -m "fix: close database connections properly"

# 4. Push и PR
git push origin fix/database-connection-leak

# 5. После merge - баг исправлен в main
```

### Пример 3: Обновление документации

```bash
# 1. Ветка
git checkout -b docs/update-api-guide

# 2. Обновить документацию
# ... edit docs ...

# 3. Коммит
git commit -m "docs: add examples for API authentication"

# 4. Push и PR
git push origin docs/update-api-guide

# 5. CI проверит что документация корректна
# 6. После merge - docs обновлены
```

## Best Practices

### Для авторов PR:

1. ✅ **Маленькие PR** - < 500 строк, одна логическая задача
2. ✅ **Self-review** - проверьте diff перед отправкой
3. ✅ **Описание** - объясните контекст и решение
4. ✅ **Тесты** - добавьте тесты для изменений
5. ✅ **CI зеленый** - исправьте все ошибки
6. ✅ **Respond быстро** - отвечайте на review комментарии оперативно

### Для reviewers:

1. ✅ **Своевременно** - review в течение 24 часов
2. ✅ **Конструктивно** - предлагайте решения, не только критикуйте
3. ✅ **Фокус на важном** - не nitpicking по мелочам
4. ✅ **Проверка кода** - запустите локально если нужно
5. ✅ **Approve или Request changes** - будьте ясны в намерениях

### Общие правила:

1. ✅ **Никогда не force push** после отправки PR (перезапишет историю)
2. ✅ **Delete branch** после merge (чистота репозитория)
3. ✅ **Закрывайте issues** через commit message: `Closes #123`
4. ✅ **Rebase на main** если ваша ветка отстала (перед final review)

## Troubleshooting

### PR показывает конфликты

```bash
# 1. Обновите main локально
git checkout main
git pull origin main

# 2. Вернитесь в feature ветку
git checkout feature/my-feature

# 3. Rebase на main
git rebase main

# 4. Разрешите конфликты
# ... edit files ...
git add .
git rebase --continue

# 5. Force push (только для feature веток!)
git push origin feature/my-feature --force-with-lease
```

### CI падает только на PR, локально работает

```bash
# 1. Проверьте окружение CI (ubuntu-latest)
# 2. Убедитесь что все зависимости в pyproject.toml/package.json
# 3. Проверьте что .gitignore не исключает нужные файлы
# 4. Запустите локально через act (эмулятор GitHub Actions)
act pull_request
```

### PR слишком большой для review

```bash
# Разбейте на несколько PR:

# 1. Refactoring сначала
git checkout -b refactor/extract-services
# ... только refactoring ...
git push origin refactor/extract-services
# [Создать PR #1, смержить]

# 2. Новая функциональность потом
git checkout -b feature/add-new-feature
# ... new feature на базе refactoring ...
git push origin feature/add-new-feature
# [Создать PR #2]
```

## Полезные ссылки

- [GitHub PR Documentation](https://docs.github.com/en/pull-requests)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
- [Squash vs Merge vs Rebase](https://blog.git-init.com/squash-vs-merge-vs-rebase/)

---

**Следующие шаги:**
- [Настройка GitHub Container Registry](github-registry-setup.md)
- [Тестирование CI/CD](ci-testing-guide.md)

