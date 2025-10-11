# 🔧 План устранения технического долга

## 📊 Отчет по прогрессу

| Итерация | Фокус | Статус | Дата завершения | Результат |
|----------|-------|--------|-----------------|-----------|
| **#1** | Автоматизация качества кода | ✅ Завершено | 2025-10-11 | Установлены ruff 0.14.0 и mypy 1.18.2. Код отформатирован, 42 проблемы линтера исправлены автоматически. Добавлены type hints. Coverage 97.78% (исключены main.py и telegram_bot.py). Все 64 теста passed. `make quality` работает! |
| **#2** | Рефакторинг MessageHandler | ✅ Завершено | 2025-10-11 | Созданы MessageExtractor и BotMessages. Устранено дублирование кода (DRY). Все hardcoded строки вынесены в константы. MessageHandler упрощен (-33 строки). Добавлено 24 новых теста. Coverage 97.99%. Все 88 тестов passed. `make quality` работает! |
| **#3** | Async/Sync + константы | ⏳ Ожидание | - | - |
| **#4** | Расширение тестирования | ⏳ Ожидание | - | - |

**Легенда статусов:**  
⏳ Ожидание | 🔄 В работе | ✅ Завершено | ⚠️ Проблемы | ❌ Отменено

---

## 🚀 Итерации устранения технического долга

### Итерация #1: Автоматизация качества кода
**Цель:** Внедрить инструменты автоматизации (линтеры, форматтеры, type checking)

**Задачи:**
- [x] Добавить `ruff>=0.1.0` в `pyproject.toml` (dev dependencies)
- [x] Добавить `mypy>=1.7.0` в `pyproject.toml` (dev dependencies)
- [x] Настроить `[tool.ruff]` секцию в `pyproject.toml`
  - line-length = 100
  - select = ["E", "F", "I", "N", "W", "B", "C90", "UP"]
- [x] Настроить `[tool.ruff.format]` в `pyproject.toml`
- [x] Настроить `[tool.mypy]` в `pyproject.toml` (strict mode)
- [x] Настроить `[tool.coverage.run]` с `fail_under = 95`
- [x] Добавить в `Makefile`:
  - `lint`: запуск ruff check
  - `format`: запуск ruff format
  - `type-check`: запуск mypy
  - `quality`: комплексная проверка (format + lint + type-check + test)
- [x] Запустить `make format` и исправить все форматирование
- [x] Запустить `make lint` и исправить все линтер-ошибки
- [x] Запустить `make type-check` и добавить type hints где необходимо
- [x] Обновить `.cursor/rules/*.mdc` и `docs/vision.md` на соответствие изменениям
- [x] Запустить `make quality` - все должно пройти

**Тест:** `make quality` проходит без ошибок, coverage >= 80%

**Acceptance Criteria:**
- ✅ Все инструменты установлены и настроены
- ✅ Код отформатирован через ruff
- ✅ Нет линтер-ошибок
- ✅ Mypy проходит в strict mode
- ✅ Coverage >= 80%

---

### Итерация #2: Рефакторинг MessageHandler (SRP, DRY)
**Цель:** Разделить ответственность MessageHandler, устранить дублирование кода

**Задачи:**
- [x] Создать `src/message_extractor.py`:
  - Класс `MessageContext` (dataclass)
  - Класс `MessageExtractor` с методом `extract()`
- [x] Создать `src/messages.py`:
  - Класс `BotMessages` с константами всех текстовых сообщений
  - Статический метод `error(error_type)` для сообщений об ошибках
- [x] Рефакторить `MessageHandler`:
  - Использовать `MessageExtractor` вместо дублирования извлечения user_id/username
  - Заменить все hardcoded строки на `BotMessages`
  - Упростить методы, убрав повторяющийся код
- [x] Создать тесты для `MessageExtractor`
- [x] Создать тесты для `BotMessages`
- [x] Обновить существующие тесты `MessageHandler` под новую структуру
- [x] Запустить `make test` - все тесты должны пройти
- [x] Запустить `make quality` - проверка качества кода
- [x] Обновить `.cursor/rules/*.mdc` и `docs/vision.md` на соответствие изменениям

**Тест:** MessageHandler стал проще, нет дублирования кода, все тесты проходят

**Acceptance Criteria:**
- ✅ MessageHandler соответствует Single Responsibility Principle
- ✅ Нет дублирования кода (DRY)
- ✅ Все строки вынесены в BotMessages
- ✅ Покрытие тестами >= 80%

---

### Итерация #3: Async/Sync исправление + вынос констант
**Цель:** Исправить синхронный вызов OpenAI в async контексте

**Задачи:**
- [ ] Рефакторить `OpenAIClient`:
  - Переименовать `send_message()` в `_sync_send_message()`
  - Создать новый async `send_message()` с использованием `run_in_executor`
  - Добавить необходимые импорты (`asyncio`, `functools.partial`)
- [ ] Обновить вызовы в `MessageHandler`:
  - Изменить `self._openai_client.send_message()` на `await self._openai_client.send_message()`
- [ ] Обновить тесты `OpenAIClient`:
  - Добавить async тесты для нового метода
  - Проверить работу executor
- [ ] Обновить тесты `MessageHandler`:
  - Адаптировать моки под async/await
- [ ] Запустить `make test` - все тесты должны пройти
- [ ] Запустить `make type-check` - проверить типизацию
- [ ] Запустить `make quality` - комплексная проверка
- [ ] Обновить `.cursor/rules/*.mdc` и `docs/vision.md` на соответствие изменениям

**Тест:** OpenAI вызовы асинхронные, не блокируют event loop

**Acceptance Criteria:**
- ✅ OpenAIClient.send_message() является async методом
- ✅ Синхронные операции выполняются в executor
- ✅ Все тесты проходят
- ✅ Mypy не выдает ошибок типизации

---

### Итерация #4: Расширение тестирования
**Цель:** Добавить интеграционные и property-based тесты

**Задачи:**
- [ ] Добавить `hypothesis>=6.0.0` в `pyproject.toml` (dev dependencies)
- [ ] Создать `tests/test_context_manager_property.py`:
  - Property-based тесты для ContextManager
  - Проверка что контекст никогда не превышает max_messages
  - Проверка инвариантов при различных сценариях
- [ ] Создать `tests/test_integration.py`:
  - Тест полного потока: message → handler → llm → storage
  - Тест сценария с ошибкой LLM
  - Тест команды /reset с проверкой очистки всех компонентов
- [ ] Создать `tests/test_telegram_bot.py`:
  - Тесты для регистрации handlers
  - Тесты для инициализации бота
- [ ] Настроить pytest markers в `pyproject.toml`:
  - `@pytest.mark.unit` для юнит-тестов
  - `@pytest.mark.integration` для интеграционных
  - `@pytest.mark.property` для property-based
- [ ] Добавить в `Makefile`:
  - `test-unit`: только юнит-тесты
  - `test-integration`: только интеграционные
  - `test-property`: только property-based
  - `test-all`: все тесты (существующий `test`)
- [ ] Запустить `make test-all` - все тесты должны пройти
- [ ] Проверить coverage >= 85%
- [ ] Запустить `make quality` - финальная проверка
- [ ] Обновить `.cursor/rules/*.mdc` и `docs/vision.md` на соответствие изменениям

**Тест:** Расширенное покрытие тестами, включая интеграционные сценарии

**Acceptance Criteria:**
- ✅ Property-based тесты для критичных компонентов
- ✅ Интеграционные тесты для основных сценариев
- ✅ Тесты для TelegramBot
- ✅ Coverage >= 85%
- ✅ Все категории тестов можно запускать отдельно

---

## 📝 Примечания

- **Каждая итерация должна заканчиваться работающим ботом** - не ломаем функциональность
- **После каждой итерации запускаем `make quality`** - проверяем что всё работает
- **Обязательно обновляем документацию** - `.mdc` файлы и `vision.md` должны быть актуальными
- **Покрытие тестами важно** - не снижаем существующий уровень
- **Следуем принципу постепенных улучшений** - маленькие шаги лучше больших рефакторингов

---

## 🎯 Конечная цель

По завершению всех итераций проект должен иметь:
- ✅ Автоматизированный контроль качества кода (ruff + mypy)
- ✅ Чистую архитектуру с соблюдением SOLID и DRY
- ✅ Правильную async/await архитектуру
- ✅ Высокое покрытие тестами (>85%)
- ✅ Интеграционные и property-based тесты
- ✅ Актуальную документацию

**Команда для проверки качества:** `make quality`

