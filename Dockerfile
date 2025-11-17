FROM python

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Создаем директорию для SSL сертификатов
RUN mkdir -p /certs

# Копируем код проекта
COPY . .

# Копируем SSL сертификаты (если директория certs/ существует и содержит файлы)
# Если лень возиться с сертификатами, можно просто закомментировать строку ниже - код будет работать с verify=False
COPY certs/ /certs/

# Печатаем все что пишет Python в stdout/stderr и не мусорим .pyc файлами в контейнере.
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# По умолчанию запускаем тесты с Allure
# Переменные окружения должны быть переданы через docker run -e или docker-compose
CMD ["pytest", "-v", "-m", "gigachat", "--alluredir=allure-results", "--tb=short"]