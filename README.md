# 2D Engine · AI Service

Separate service that creates game objects for the 2D engine and **learns from every run**
played on a level, so the obstacles it places get harder (or easier) to keep the level fun.
Only the backend calls it; the frontend never talks to it.

```
Frontend -> Backend -> Database (stores each level's learned model)
               |
               +-- service token (JWT, 60 s) --> AI Service -> optional external AI API
```

## API

| Route | What it does |
|---|---|
| `GET /health` | Liveness check (no token) |
| `POST /generate` | `{prompt, scene}` → objects described by the text, pushed off existing objects by the physics engine |
| `POST /learn` | `{model, run}` → updated model, reward and new difficulty |
| `POST /obstacles` | `{model, scene, count?}` → obstacles placed with the learned model |
| `GET /info` | World size, kinds, object sizes and the default model |

Every route except `/health` needs `Authorization: Bearer <service token>`.

## How it is organised

| Code | Role |
|---|---|
| `app/world.py` | World size (1600 × 960, tiles of 32), kinds and their sizes; same values as the backend and frontend |
| `app/physics/` | `AABB`, `Body`, `PhysicsWorld`: Arcade-style velocity, drag, bounds and collision separation |
| `app/navigation/` | `OccupancyGrid` and breadth-first search: which coins the player can reach |
| `app/learning/` | `LevelModel`, `RunFeatures`, `reward`, `Learner`: online learning from runs |
| `app/generation/` | `ObstacleGenerator`: places obstacles following the model and the physics rules |
| `app/agent.py` | `GameAgent`: builds the prompt, validates the model's reply and fixes overlaps |
| `app/providers/` | `simulated` (no network) or `openai_compatible` (any `/chat/completions` API) |
| `app/security.py` | Checks the service token: signature, audience, issuer, expiry and replay |
| `app/hardening.py` | Security headers, 1 MB body limit and start-up check of the key |
| `app/main.py`, `app/learning_api.py` | The HTTP routes |

## How the AI learns

Each finished run becomes a performance score between 0 and 1 (winning, coins, damage,
deaths). The AI is rewarded when that score lands near **0.65**: hard but fair.

- Played too well → difficulty goes up → more obstacles (4 to 20) placed closer to the coins.
- Struggled → difficulty goes down.
- Enemies and spikes did not hurt → they get picked more; they overwhelmed the player → less.
- Coins were hard to reach → fewer walls and houses.

The step size shrinks as runs pile up (0.3 / √(runs + 1), at least 0.05). Details and the
exact numbers are in [docs/learning.md](docs/learning.md).

## Physics rules the generator follows

- Every obstacle is inside the world and does not overlap anything (AABB with a 4 px gap).
- Nothing within 128 px of the player's spawn point, and no enemy within 256 px.
- A solid obstacle (box, wall, house, tree) is rejected if it cuts off a coin the player could reach.
- Objects asked for with `/generate` are pushed out of what already exists, like Arcade Physics would.
- Same scene and same model give the same obstacles, so results are repeatable.

## Run locally (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest
copy .env.example .env     # then edit AI_SERVICE_KEY (same value as in the backend)
python -m uvicorn app.main:app --port 8001 --reload
```

## Environment variables

| Variable | Meaning |
|---|---|
| `AI_SERVICE_KEY` | Shared secret (32+ characters). The backend signs a 60-second JWT with it for every call. |
| `AI_PROVIDER` | `simulated` (default) or `openai_compatible` |
| `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL` | Only for `openai_compatible`; a missing one gives a clear 503 |

## Deployment (Render)

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set the environment variables above in the service settings, never in the code.
- No CORS is enabled on purpose, so browsers cannot call this service.
- The replay check keeps used token ids in memory; run one instance (or put the ids in a shared store).
- Set `ENVIRONMENT=production`: the service then refuses to start with a weak or example key and hides `/docs`.
