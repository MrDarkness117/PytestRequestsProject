FROM python

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /certs

COPY . .

COPY certs/ /certs/

# Печатаем все что пишет Python в stdout/stderr и не мусорим .pyc файлами в контейнере.
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["pytest", "-v", "-m", "gigachat", "--alluredir=allure-results", "--tb=short"]
