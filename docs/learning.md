# How the AI learns

The service keeps no state. The backend stores one **level model** per project
(`ai_models.parameters`) and sends it with every request; the service returns the updated one.

```json
{
  "difficulty": 0.5, "runs": 0,
  "win_rate": 0.5, "coin_ratio": 0.5, "damage": 0.0, "run_seconds": 60.0,
  "weights": {"box": 1.0, "wall": 1.0, "tree": 0.7, "house": 0.3, "spike": 0.5, "enemy": 0.6},
  "version": 1
}
```

Anything missing or out of range in that JSON falls back to these defaults, so a corrupted
row can never break the service.
