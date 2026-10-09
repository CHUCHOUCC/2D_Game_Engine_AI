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
| `app/main.py`, `app/learning_api.py` | The HTTP routes |
