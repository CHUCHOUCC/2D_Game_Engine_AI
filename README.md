# 2D Engine · AI Service

Separate service that creates game objects from a natural-language request.
Only the backend calls it; the frontend never talks to it.

```
Frontend -> Backend -> Database
               |
               +-----> AI Service -> external AI API
```

## How it is organised

| Code | Role |
|---|---|
| `app/providers/base.py` | `AiProvider`: the contract every provider follows |
| `app/providers/simulated.py` | Deterministic provider for demos and tests (no network, no key) |
| `app/providers/openai_compatible.py` | Real provider for any `/chat/completions` API |
| `app/providers/__init__.py` | `create_provider()`: picks the provider from `AI_PROVIDER` |
| `app/agent.py` | `GameAgent`: builds the prompt and **validates** the model's reply |
| `app/security.py` | Service-key check: only the backend can call `/generate` |
| `app/main.py` | `GET /health`, `POST /generate` |

Changing the AI API means changing environment variables (or adding one provider class); the agent and the API do not change.

## Run locally (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest
copy .env.example .env     # then edit AI_SERVICE_KEY
python -m uvicorn app.main:app --port 8001 --reload
```

## Environment variables

| Variable | Meaning |
|---|---|
| `AI_SERVICE_KEY` | Shared secret. The backend sends it in the `X-Service-Key` header. |
| `AI_PROVIDER` | `simulated` (default) or `openai_compatible` |
| `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL` | Only for `openai_compatible` |

## Deployment (Render)

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set the environment variables above in the service settings, never in the code.
- No CORS is enabled on purpose, so browsers cannot call this service.
