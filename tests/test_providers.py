import json

import httpx
import pytest

from app.providers import (
    AiProviderError,
    OpenAiCompatibleProvider,
    SimulatedProvider,
    create_provider,
)


def provider_with(handler):
    return OpenAiCompatibleProvider(
        base_url="https://api.example.com/v1/",
        api_key="secret-key",
        model="some-model",
        transport=httpx.MockTransport(handler),
    )


def test_openai_compatible_sends_the_expected_request_and_returns_the_text():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})

    reply = provider_with(handler).complete("be brief", "hi")

    assert reply == "hello"
    assert seen["url"] == "https://api.example.com/v1/chat/completions"
    assert seen["auth"] == "Bearer secret-key"
    assert seen["body"]["model"] == "some-model"
    assert seen["body"]["messages"][0] == {"role": "system", "content": "be brief"}
    assert seen["body"]["messages"][1] == {"role": "user", "content": "hi"}


def test_http_error_becomes_provider_error():
    provider = provider_with(lambda request: httpx.Response(500))
    with pytest.raises(AiProviderError):
        provider.complete("s", "u")


def test_unexpected_reply_shape_becomes_provider_error():
    provider = provider_with(lambda request: httpx.Response(200, json={"unexpected": True}))
    with pytest.raises(AiProviderError):
        provider.complete("s", "u")


def test_factory_defaults_to_simulated(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    assert isinstance(create_provider(), SimulatedProvider)


def test_factory_builds_the_real_provider_from_environment(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai_compatible")
    monkeypatch.setenv("AI_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("AI_API_KEY", "k")
    monkeypatch.setenv("AI_MODEL", "m")
    assert isinstance(create_provider(), OpenAiCompatibleProvider)


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError):
        create_provider("nope")


def test_factory_reports_missing_settings(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai_compatible")
    monkeypatch.setenv("AI_BASE_URL", "https://api.example.com/v1")
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("AI_MODEL", raising=False)
    with pytest.raises(AiProviderError, match="AI_API_KEY, AI_MODEL"):
        create_provider()


def test_network_failure_becomes_provider_error():
    def handler(request):
        raise httpx.ConnectError("unreachable")

    with pytest.raises(AiProviderError):
        provider_with(handler).complete("s", "u")
