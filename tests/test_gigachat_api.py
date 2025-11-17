import json

import re
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

    response_dict = dict()

    def fill_response_dict(self, response, model):
        """
        Заполняем словарь ответами для разных моделей
        """
        self.response_dict[model] = response["choices"][0]["message"]["content"]
        if len(self.response_dict) == 3:
            return (True, self.response_dict)
        return (False, None)

    @allure.title("Базовый ответ на простое пользовательское сообщение")
    @allure.description("""Базовый тест: отправка простого сообщения и проверка успешного ответа""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_basic(self, api_base_url, api_headers, verify_ssl):
        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": "Привет! Как дела?"
                }
            ],
            "temperature": 0.7
        }

        with allure.step("Отправляем запрос к GigaChat API"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})
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
    def test_chat_completions_with_system_message(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
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
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем статус и роль ответа"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)
            assert data["choices"][0]["message"]["role"] == "assistant"

    @allure.title("Диалог из нескольких сообщений в рамках одной сессии")
    @allure.description("""Тест: диалог с несколькими сообщениями""")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_multiple_messages(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": "Привет, меня зовут Миша"
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
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

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
        
        Наблюдения: чем выше температура, тем дольше модель думает над ответом
        """)
    @pytest.mark.parametrize("temperature", [0.00005, 0.0001, 0.1, 0.5, 0.9, 1.0, 1.5, 2.0,
                                             pytest.param(2.4, marks=pytest.mark.xfail(reason='Иногда возникает ошибка 500'))])
    def test_chat_completions_temperature(self, api_base_url, api_headers, temperature, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": "Расскажи коротко о погоде в Москве сегодня"
                }
            ],
            "temperature": temperature
        }

        with allure.step(f"Отправляем запрос с temperature={temperature}"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем успешность ответа и структуру"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)

    @allure.title("Ограничение максимального количества токенов в ответе")
    @allure.description("""Тест: проверка ограничения максимального количества токенов в ответе""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_max_tokens(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": "Расскажи подробно о программировании"
                }
            ],
            "max_tokens": 50
        }

        with allure.step("Отправляем запрос с ограничением max_tokens=50"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

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
    @pytest.mark.xfail
    def test_chat_completions_empty_message(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": ""
                }
            ]
        }

        with allure.step("Отправляем запрос с пустым сообщением"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем, что API возвращает ожидаемую ошибку"):
            assert response.status_code in [422]

    @allure.title("Обработка невалидной модели")
    @allure.description("""Тест: проверка обработки невалидной модели""")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_invalid_model(self, api_base_url, api_headers, verify_ssl):

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
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем, что возвращается один из ожидаемых кодов ошибки"):
            assert response.status_code in [400, 404, 422]

    @allure.title("Обработка отсутствующей модели")
    @allure.description("""Тест: проверка обработки отсутствующей модели""")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chat_completions_undefined_model(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "",
            "messages": [
                {
                    "role": "user",
                    "content": "Тест"
                }
            ]
        }

        with allure.step("Отправляем запрос с отсутствующей моделью"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем, что возвращается один из ожидаемых кодов ошибки"):
            assert response.status_code in [400, 404, 422]

    @allure.title("Проверка различных моделей")
    @allure.description("""Тест: параметризованная проверка различных моделей""")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("model", ["GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max"])
    def test_chat_completions_different_models(self, api_base_url, api_headers, model, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": """
                    Давай пофантазируем! Как думаешь, что говорит о человеке то, с каким персонажем из 
                    Baldur's Gate 3 он решил устроить романтическую линию?"""
                }
            ]
        }

        with allure.step("Отправляем запрос для проверки различных моделей"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем статус и структуру ответа"):
            assert response.status_code == 200, (
                f"Ожидался статус 200, получен {response.status_code}."
            )
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)
        
        with allure.step("Проверяем, что ответ уникален для данной модели"):
            content = data["choices"][0]["message"]["content"]
            self.fill_response_dict(data, model)
        
            if self.response_dict:
                previous_contents = [v for k, v in self.response_dict.items() if k != model]
                assert content not in previous_contents, (
                    f"Ответ для модели {model} совпадает с предыдущими ответами. "
                    f"Текущий ответ: '{content[:100]}...'"  # Урежем чтобы не захламлять отчет
                )


    @allure.title("Детальная проверка структуры и usage")
    @allure.description("""Тест: детальная проверка структуры ответа""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_response_structure(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": "Ответь одним словом: да или нет?"
                }
            ]
        }

        with allure.step("Отправляем запрос для детальной проверки структуры"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем статус и структуру ответа"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)

        with allure.step("Проверяем логику ответа и usage"):
            assert data["choices"][0]["message"]["role"] == "assistant", "Роль ответа должна быть assistant"
            assert data["usage"]["total_tokens"] == data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"]

    @allure.title("Проверка поддержки мультиязычности")
    @allure.description("""Тест: проверяем, проддерживает ли модель мультиязычность""")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_completions_multilingual_support(self, api_base_url, api_headers, verify_ssl):

        url = f"{api_base_url}/chat/completions"
        payload = {
            "model": "GigaChat-2",
            "messages": [
                {
                    "role": "user",
                    "content": "Please respond to me in English: Good day to you. How are you?"
                }
            ]
        }

        with allure.step("Отправляем запрос с мультиязычным сообщением"):
            response = requests.post(url, json=payload, headers=api_headers, verify=verify_ssl, proxies={'http': None, 'https': None})

        with allure.step("Проверяем, что ответ содержит текст на английском языке"):
            assert response.status_code == 200
            data = response.json()
            validate(instance=data, schema=schema_chat_completion)
            assert re.search(r'[a-zA-Z]', data["choices"][0]["message"]["content"]) is not None, "Ответ должен содержать текст на английском языке"