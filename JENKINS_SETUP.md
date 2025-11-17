# Инструкция по настройке Jenkins для проекта GigaChat API Tests

## Быстрый старт

### 1. Установка необходимых плагинов

В Jenkins перейдите в `Manage Jenkins` → `Manage Plugins` → `Available` и установите:

- **Allure Plugin** — для генерации и отображения Allure отчетов
- **Pipeline Plugin** (обычно уже установлен) — для работы с Jenkinsfile
- **Git Plugin** (обычно уже установлен) — для работы с Git репозиторием

После установки перезапустите Jenkins.

### 2. Настройка Allure Commandline

1. Перейдите в `Manage Jenkins` → `Global Tool Configuration`
2. Найдите секцию **Allure Commandline**
3. Нажмите **Add Allure Commandline**
4. Выберите один из вариантов:
   - **Install automatically** — Jenkins скачает и установит Allure автоматически
   - **Указать путь** — если Allure уже установлен на сервере, укажите путь к исполняемому файлу
5. Сохраните настройки

### 3. Настройка переменных окружения

#### Способ 1: Jenkins Credentials (Рекомендуется)

1. Перейдите в `Manage Jenkins` → `Manage Credentials`
2. Выберите нужный домен (обычно `(global)`)
3. Нажмите **Add Credentials**
4. Выберите тип **Secret text**
5. Заполните:
   - **Secret:** ваш `GIGACHAT_BASIC_AUTH_TOKEN`
   - **ID:** `gigachat-basic-auth-token` (или любое удобное имя)
   - **Description:** `GigaChat Basic Auth Token`
6. Сохраните

#### Способ 2: Environment Variables в Job

В настройках Jenkins Job:

1. Перейдите в **Configure**
2. Найдите секцию **Build Environment**
3. Отметьте **Use secret text(s) or file(s)**
4. Добавьте **Bindings**:
   - **Variable:** `GIGACHAT_BASIC_AUTH_TOKEN`
   - **Credentials:** выберите созданный credential

Или используйте **Environment variables** (менее безопасно):

```
GIGACHAT_BASIC_AUTH_TOKEN=your_token_here
GIGACHAT_API_BASE_URL=https://gigachat.devices.sberbank.ru/api/v1
GIGACHAT_OAUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
```

### 4. Создание Jenkins Job

#### Вариант A: Pipeline Job (Рекомендуется)

1. Создайте новый **Pipeline** Job
2. В разделе **Pipeline**:
   - **Definition:** `Pipeline script from SCM`
   - **SCM:** `Git`
   - **Repository URL:** URL вашего Git репозитория
   - **Credentials:** если репозиторий приватный
   - **Branch Specifier:** `*/main` или `*/master` (или ваша ветка)
   - **Script Path:** `Jenkinsfile` (по умолчанию)
3. Сохраните

#### Вариант B: Freestyle Job

1. Создайте новый **Freestyle project**
2. В разделе **Source Code Management:**
   - Выберите `Git`
   - Укажите **Repository URL**
   - Укажите **Branch** (например, `*/main`)
3. В разделе **Build Environment:**
   - Настройте переменные окружения (см. способ 2 выше)
4. В разделе **Build:**
   - Добавьте **Execute shell** (Linux/Mac) или **Execute Windows batch command** (Windows):
   ```bash
   # Установка зависимостей
   pip install -r requirements.txt
   
   # Запуск тестов
   pytest -v -m gigachat --alluredir=allure-results --tb=short
   ```
5. В разделе **Post-build Actions:**
   - Добавьте **Publish Allure Report**
   - **Results path:** `allure-results`
6. Сохраните

### 5. Запуск и проверка

1. Нажмите **Build Now** в созданном Job
2. Дождитесь завершения сборки
3. После успешной сборки вы увидите:
   - **Allure Report** — ссылка на отчет в левом меню
   - В консоли сборки будут логи выполнения тестов

## Дополнительные настройки

### Настройка триггеров (автоматический запуск)

В настройках Job → **Build Triggers**:

- **Poll SCM** — проверка изменений в репозитории по расписанию (например, `H/15 * * * *` — каждые 15 минут)
- **GitHub hook trigger** — если используете GitHub, можно настроить webhook
- **Build periodically** — запуск по расписанию (например, `0 2 * * *` — каждый день в 2:00)

### Настройка уведомлений

Можно добавить уведомления при падении тестов:

1. Установите плагин **Email Extension Plugin**
2. В настройках Job → **Post-build Actions** → **Editable Email Notification**
3. Настройте шаблоны уведомлений

### Использование Docker (будущее)

Когда будете готовы использовать Docker:

1. Убедитесь, что на Jenkins сервере установлен Docker
2. Добавьте в Jenkinsfile шаг сборки Docker образа
3. Настройте передачу SSL сертификатов в контейнер

Пример шага в Jenkinsfile:
```groovy
stage('Build Docker Image') {
    steps {
        sh 'docker build -t gigachat-tests .'
    }
}
```

## Решение проблем

### Проблема: Allure отчет не отображается

**Решение:**
- Убедитесь, что установлен **Allure Plugin**
- Проверьте, что в **Global Tool Configuration** настроен Allure Commandline
- Проверьте, что путь `allure-results` указан правильно

### Проблема: Тесты падают с ошибкой SSL

**Решение:**
- Временно можно отключить проверку SSL (см. `conftest.py`)
- В будущем добавьте SSL сертификат через переменную `GIGACHAT_CA_BUNDLE`

### Проблема: Переменные окружения не подхватываются

**Решение:**
- Проверьте, что переменные настроены в **Build Environment**
- Убедитесь, что используется правильный синтаксис для вашей ОС (Linux/Mac vs Windows)
- Проверьте логи сборки на наличие ошибок

### Проблема: Python не найден

**Решение:**
- Убедитесь, что Python установлен на Jenkins сервере
- В Jenkinsfile измените переменную `PYTHON` на правильный путь (например, `python3`)
- Или используйте полный путь: `/usr/bin/python3`

## Полезные ссылки

- [Allure Plugin Documentation](https://plugins.jenkins.io/allure-jenkins-plugin/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Pytest Documentation](https://docs.pytest.org/)

