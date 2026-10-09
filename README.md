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
