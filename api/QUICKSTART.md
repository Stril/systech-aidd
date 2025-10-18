# Quick Start Guide - Bot Statistics API

## 🚀 Запуск за 3 шага

### 1. Установите зависимости

```bash
make install
```

### 2. Запустите API сервер

```bash
make api-run
```

Сервер запустится на `http://localhost:8000`

### 3. Откройте документацию

В браузере перейдите на: **http://localhost:8000/docs**

## ✅ Проверка работы

```bash
# В новом терминале выполните:
make api-test
```

Вы должны увидеть JSON данные для периодов day и week.

## 📊 Примеры использования

### Получить статистику за день

```bash
curl "http://localhost:8000/api/stats?period=day"
```

### Получить статистику за неделю

```bash
curl "http://localhost:8000/api/stats?period=week"
```

### PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day"
```

## 📚 Дополнительно

- **Полная документация:** [README.md](README.md)
- **Примеры на разных языках:** [EXAMPLES.md](EXAMPLES.md)
- **Результаты Sprint 1:** [SPRINT1_SUMMARY.md](SPRINT1_SUMMARY.md)

## 🎯 Для Frontend разработчиков

API готов к использованию! Вы можете:

1. Использовать TypeScript типы из [EXAMPLES.md](EXAMPLES.md)
2. Интегрироваться с любым frontend фреймворком
3. Тестировать на реалистичных данных
4. Работать независимо от backend команды

## 🛠️ Доступные команды

```bash
make api-run     # Запустить API сервер
make api-test    # Протестировать API
make api-docs    # Показать ссылки на документацию
```

## ❓ Проблемы?

1. Убедитесь что порт 8000 свободен
2. Проверьте что зависимости установлены: `make install`
3. Проверьте логи сервера при запуске

---

**Готовы? Начните с `make api-run`!** 🚀

