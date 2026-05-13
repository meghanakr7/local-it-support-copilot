from openai import OpenAI

from app.config import settings, validate_settings


class LLMClient:
    def __init__(self) -> None:
        validate_settings()

        if settings.llm_provider != "openai":
            raise ValueError(
                "Only the OpenAI provider is implemented in this development version. "
                "The architecture keeps the provider isolated so a local model adapter can be added later."
            )

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        message = response.choices[0].message.content

        if not message:
            return ""

        return message.strip()