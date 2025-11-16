# Pytest Requests Project - GigaChat API Testing

Фреймворк для автоматического тестирования GigaChat API с использованием PyTest.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` в корне проекта на основе примера:
```env
# Base URL для API (опционально, есть значения по умолчанию)
GIGACHAT_API_BASE_URL=https://gigachat.devices.sberbank.ru/api/v1
GIGACHAT_OAUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
# Токен авторизации
GIGACHAT_BASIC_AUTH_TOKEN
```

## Запуск тестов

### Запуск всех тестов GigaChat API:
```bash
pytest -v -m gigachat
```

### Запуск конкретного теста:
```bash
pytest -v tests/test_gigachat_api.py::TestGigaChatCompletions::test_chat_completions_basic
```

### Запуск всех тестов:
```bash
pytest -v
```

## Генерация Allure отчетов

Тесты уже размечены аннотациями Allure (`feature`, `story`, `severity`, шаги и вложения).

1. **Запуск тестов с генерацией Allure-результатов:**
```bash
pytest -m gigachat --alluredir=allure-results
```

2. **Быстрый просмотр отчета:**
```bash
allure serve allure-results
```

3. **Генерация статического HTML отчета:**
```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### Фильтрация тестов в Allure

В Allure вы увидите:
- **Feature:** `GigaChat API`
- **Story:** `chat/completions`
- **Severity:** `CRITICAL`, `NORMAL`, `MINOR` — для разных сценариев

Это позволяет удобно фильтровать тесты и анализировать критичные сценарии.

## Структура проекта

```
.
├── tests/
│   ├── __init__.py          # Базовые функции для работы с API
│   ├── conftest.py          # Фикстуры и настройки pytest
│   ├── schemas.py           # JSON схемы для валидации ответов
│   └── test_gigachat_api.py # Тесты для GigaChat API
├── requirements.txt         # Зависимости проекта
├── pytest.ini              # Конфигурация pytest
└── .env                    # Переменные окружения (создать самостоятельно)
```

## Тесты

Тесты для GigaChat API находятся в файле `tests/test_gigachat_api.py` и включают:

- Базовый тест отправки сообщения
- Тест с системным промптом
- Тест диалога с несколькими сообщениями
- Тесты с различными параметрами (temperature, max_tokens)
- Тесты обработки ошибок
- Детальная проверка структуры ответа

Все тесты используют валидацию JSON схем для проверки структуры ответов API.


