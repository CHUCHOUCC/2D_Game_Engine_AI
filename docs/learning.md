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

## Performance and reward

```
performance = 0.5 · won + 0.3 · coins_collected / coins_total + 0.2 · (1 − min(damage / 5, 1))
              − 0.1 · min(deaths, 3)                      (kept between 0 and 1)

reward = 1 − |performance − 0.65| / 0.65                  (halved if the player quit)
```

A perfect run (performance 1.0) only earns 0.46: the AI prefers levels that challenge the player.
