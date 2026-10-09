"""Defensive layers of the AI service: body size limit, security headers and
start-up checks. The service is only called by the backend, but it is still
reachable from the internet, so it must not trust its callers blindly."""
import json
import logging
import os

logger = logging.getLogger("app.hardening")

MAX_BODY_BYTES = 1_000_000
MIN_KEY_LENGTH = 32
PLACEHOLDER_MARKERS = ("change-me", "changeme", "example")
SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"cache-control", b"no-store"),
    (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'"),
]


def is_production() -> bool:
    return os.environ.get("ENVIRONMENT", "development").strip().lower() == "production"


def key_problems(key: str) -> list:
    if not key:
        return ["AI_SERVICE_KEY is not set"]
    problems = []
    if len(key) < MIN_KEY_LENGTH:
        problems.append(f"AI_SERVICE_KEY must have at least {MIN_KEY_LENGTH} characters")
    if any(marker in key.lower() for marker in PLACEHOLDER_MARKERS):
        problems.append("AI_SERVICE_KEY still has the example value")
    return problems


def check_configuration() -> list:
    """Refuse to start in production with a weak key; only warn in development."""
    problems = key_problems(os.environ.get("AI_SERVICE_KEY", ""))
    if problems and is_production():
        raise RuntimeError("Insecure configuration: " + "; ".join(problems))
    for problem in problems:
        logger.warning("Configuration: %s", problem)
    return problems


class HardeningMiddleware:
    """Adds the security headers and refuses bodies over MAX_BODY_BYTES (413)."""

    def __init__(self, app, max_bytes: int = MAX_BODY_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        for name, value in scope.get("headers", []):
            if name == b"content-length" and value.isdigit() and int(value) > self.max_bytes:
                await _reply(send, 413, {"detail": "Request body too large"})
                return

        is_docs = scope["path"].startswith(("/docs", "/openapi.json"))

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                for name, value in SECURITY_HEADERS:
                    if is_docs and name == b"content-security-policy":
                        continue
                    headers.append((name, value))
            await send(message)

        await self.app(scope, receive, send_with_headers)


async def _reply(send, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode()
    headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
    await send({"type": "http.response.start", "status": status, "headers": headers + SECURITY_HEADERS})
    await send({"type": "http.response.body", "body": body})
