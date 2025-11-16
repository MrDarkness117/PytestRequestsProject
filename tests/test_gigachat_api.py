import json

import allure
import pytest
import requests
from jsonschema import validate

from .schemas import schema_chat_completion


@pytest.mark.gigachat
@allure.feature("GigaChat API")
@allure.story("chat/completions")
class TestGigaChatCompletions:
    """Тестовый набор для метода chat/completions GigaChat API"""

    @allure.title("Базовый ответ на простое пользовательское сообщение")
    @allure.description("""Базовый тест: отправка простого сообщения и проверка успешного ответа""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_basic(self, api_base_url, api_headers):
        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": "Привет! Как дела?"
                }
            ],
            "temperature": 0.7
        }

        with allure.step("Отправляем запрос к GigaChat API"):
            response = requests.post(url, json=payload, headers=api_headers)
            # Прикрепляем запрос/ответ к отчету
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2),
                          name="request_body",
                          attachment_type=allure.attachment_type.JSON)
            allure.attach(response.text,
                          name="response_body",
                          attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверяем HTTP статус и структуру ответа"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, получен {response.status_code}. Ответ: {response.text}"
            )
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)

        with allure.step("Проверяем, что ответ содержит текст"):
            assert len(data["choices"][0]["message"]["content"]) > 0, "Ответ должен содержать текст"

    @allure.title("Ответ с учетом системного промпта")
    @allure.description("""Тест: отправка сообщения с системным промптом""")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_with_system_message(self, api_base_url, api_headers):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты полезный ассистент, который отвечает кратко и по делу."
                },
                {
                    "role": "user",
                    "content": "Что такое GigaChat?"
                }
            ]
        }

        with allure.step("Отправляем запрос с системным промптом"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем статус и роль ответа"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)
            assert data["choices"][0]["message"]["role"] == "assistant"

    @allure.title("Диалог из нескольких сообщений в рамках одной сессии")
    @allure.description("""Тест: диалог с несколькими сообщениями""")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_multiple_messages(self, api_base_url, api_headers):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": "Привет, меня зовут Иван"
                },
                {
                    "role": "assistant",
                    "content": "Привет, Иван! Как дела?"
                },
                {
                    "role": "user",
                    "content": "Отлично, спасибо!"
                }
            ]
        }

        with allure.step("Отправляем запрос с несколькими сообщениями"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем, что токены были использованы"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)
            assert data["usage"]["total_tokens"] > 0

    @allure.title("Разные значения temperature")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("""Тест: проверка работы с разными значениями temperature.
        Используем от 0.00005 до 2.6 так как в документации указано, что значения от 0.0 до 0.0001, то параметры
        temperature и top_p будут сброшены в режим, обеспечивающий максимально детерминированный (стабильный) ответ
        модели. Аналогично для значений от 2.0 - набор токенов в ответе модели может отличаться избыточной случайностью.
        """)
    @pytest.mark.parametrize("temperature", [0.00005, 0.0001, 0.1, 0.5, 0.9, 1.0, 1.5, 2.0, 2.6])
    def test_chat_completions_temperature(self, api_base_url, api_headers, temperature):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": "Расскажи коротко о погоде в Москве сегодня"
                }
            ],
            "temperature": temperature
        }

        with allure.step(f"Отправляем запрос с temperature={temperature}"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем успешность ответа и структуру"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)

    @allure.title("Ограничение максимального количества токенов в ответе")
    @allure.description("""Тест: проверка ограничения максимального количества токенов в ответе""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_max_tokens(self, api_base_url, api_headers):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": "Расскажи подробно о программировании"
                }
            ],
            "max_tokens": 50
        }

        with allure.step("Отправляем запрос с ограничением max_tokens=50"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем, что лимит токенов не превышен"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)
            assert data["usage"]["completion_tokens"] <= 50

    @allure.title("Обработка пустого сообщения")
    @allure.description("""
        Тест: проверка обработки пустого сообщения.
        Мы ожидаем, что API вернет ошибку 422, так как пустое сообщение не является валидным.
        """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_empty_message(self, api_base_url, api_headers):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": ""
                }
            ]
        }

        with allure.step("Отправляем запрос с пустым сообщением"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем, что API возвращает ожидаемую ошибку"):
            assert response.status_code in [422]

    @allure.title("Обработка невалидной модели")
    @allure.description("""Тест: проверка обработки невалидной модели""")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_invalid_model(self, api_base_url, api_headers):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "InvalidModel",
            "messages": [
                {
                    "role": "user",
                    "content": "Тест"
                }
            ]
        }

        with allure.step("Отправляем запрос с невалидной моделью"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем, что возвращается один из ожидаемых кодов ошибки"):
            assert response.status_code in [400, 404, 422]

    @allure.title("Детальная проверка структуры и usage")
    @allure.description("""Тест: детальная проверка структуры ответа""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_response_structure(self, api_base_url, api_headers):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": "Ответь одним словом: да или нет?"
                }
            ]
        }

        with allure.step("Отправляем запрос для детальной проверки структуры"):
            response = requests.post(url, json=payload, headers=api_headers)

        with allure.step("Проверяем статус и структуру ответа"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)

        with allure.step("Проверяем логику ответа и usage"):
            assert data["choices"][0]["message"]["role"] == "assistant", "Роль ответа должна быть assistant"
            assert data["usage"]["total_tokens"] == data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"]

