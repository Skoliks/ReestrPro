from gigachat import GigaChat

from backend.core.config import settings


class LLMClient:
    def __init__(self) -> None:
        if not settings.gigachat_credentials:
            raise ValueError(
                "GIGACHAT_CREDENTIALS не задан в .env. "
                "Укажите ключ авторизации GigaChat."
            )

        self.credentials = settings.gigachat_credentials
        self.model = settings.gigachat_model
        self.verify_ssl_certs = settings.gigachat_verify_ssl_certs

    def generate_answer(self, question: str, context: str) -> str:
        prompt = self._build_prompt(question=question, context=context)

        with GigaChat(
            credentials=self.credentials,
            verify_ssl_certs=self.verify_ssl_certs,
        ) as client:
            response = client.chat(
                {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Ты помощник для анализа сертификатов и деклараций "
                                "соответствия. Отвечай только на основе переданного "
                                "контекста. Если данных недостаточно, прямо скажи об этом. "
                                "Не придумывай факты."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    "temperature": 0.2,
                }
            )

        return response.choices[0].message.content

    @staticmethod
    def _build_prompt(question: str, context: str) -> str:
        return f"""
Вопрос пользователя:
{question}

Контекст из найденных документов:
{context}

Сформируй краткое объяснение:
1. Какие документы найдены.
2. Почему они могут соответствовать запросу.
3. Какие признаки совпали.
4. Что нужно дополнительно проверить вручную.

Отвечай на русском языке.
"""