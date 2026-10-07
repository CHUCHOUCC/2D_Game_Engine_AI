import httpx

from .base import AiProvider, AiProviderError


class OpenAiCompatibleProvider(AiProvider):
    """Provider for any API that speaks the widely used /chat/completions format.

    Many services offer it (OpenAI, Groq, OpenRouter, Gemini's compatibility
    endpoint...). Switching service is only a matter of base_url, model and key.
    """

    def __init__(self, base_url: str, api_key: str, model: str, transport=None, timeout: float = 30.0):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._transport = transport
        self._timeout = timeout

    def complete(self, system: str, user: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            with httpx.Client(transport=self._transport, timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as error:
            raise AiProviderError(f"AI provider call failed: {type(error).__name__}") from error
