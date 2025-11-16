import os
import uuid
import pytest
from dotenv import load_dotenv
import requests

# Загружаем переменные окружения из .env файла
load_dotenv()

GIGACHAT_BASIC_AUTH_TOKEN = os.getenv('GIGACHAT_BASIC_AUTH_TOKEN')
GIGACHAT_API_BASE_URL = os.getenv('GIGACHAT_API_BASE_URL', 'https://gigachat.devices.sberbank.ru/api/v1')
GIGACHAT_OAUTH_URL = os.getenv('GIGACHAT_OAUTH_URL', 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth')

from . import BASEURL_API


# def pytest_addoption(parser):
#     parser.addoption("--api", dest="api", type="string",
#                       action="store", default="", help="")
#     parser.addoption("--hash", dest="hash", type="string",
#                       action="store", default="", help="")
#
#
# def pytest_generate_tests(metafunc):
#     if 'api' in metafunc.fixturenames:
#         metafunc.parametrize("api", [metafunc.config.getoption('api')])
#
#     if 'hash' in metafunc.fixturenames:
#         metafunc.parametrize("hash", [metafunc.config.getoption('hash')])


def get_token():
    """
    Получает OAuth токен для доступа к GigaChat API.
    Возвращает access_token из ответа API.
    """
    
    if not GIGACHAT_BASIC_AUTH_TOKEN:
        raise ValueError(
            "Необходимо установить GIGACHAT_BASIC_AUTH_TOKEN в .env файле"
        )
    auth_header = f'Basic {GIGACHAT_BASIC_AUTH_TOKEN}'
    
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': auth_header
    }
    
    response = requests.post(GIGACHAT_OAUTH_URL, headers=headers, data=payload)
    response.raise_for_status()  # Вызовет исключение при ошибке HTTP
    
    response_data = response.json()
    access_token = response_data.get('access_token')
    
    if not access_token:
        raise ValueError(f"Токен не найден в ответе API: {response_data}")
    
    return access_token


@pytest.fixture(scope="session")
def access_token():
    """
    Фикстура для получения access token.
    Токен кэшируется на время сессии тестов.
    """
    return get_token()


@pytest.fixture(scope="session")
def api_base_url():
    """
    Фикстура для базового URL API GigaChat.
    """
    return GIGACHAT_API_BASE_URL


@pytest.fixture(scope="function")
def api_headers(access_token):
    """
    Фикстура для заголовков запросов к API GigaChat.

    X-Request-ID: Обязательный заголовок для каждого запроса
    X-Session-ID: Обязательный заголовок, позволяет сохранять контекст сессии
    """
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Request-ID': str(uuid.uuid4()),
        'X-Session-ID': str(uuid.uuid4())
    }

