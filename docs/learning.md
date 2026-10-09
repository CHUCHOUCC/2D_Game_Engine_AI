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

## One learning step (`POST /learn`)

1. `rate = max(0.05, 0.3 / √(runs + 1))`
2. Moving averages of win rate, coin ratio, damage and time (30 % weight for the new run).
3. `difficulty += 2 · rate · (performance − 0.65)`, kept between 0.05 and 0.95.
4. Kind weights:

| What happened | Change |
|---|---|
| Won with little damage | enemy, spike × (1 + rate) |
| Lost with heavy damage | enemy, spike × (1 − rate/2) |
| Lost and took less than half the coins | wall, house × (1 − rate/2) |
| Won and took every coin | wall, box × (1 + rate/2) |
| Defeated 3+ enemies | enemy × (1 + rate/2) |

## Placing obstacles (`POST /obstacles`)

- How many: `count`, or the model's budget `round(4 + 16 · difficulty)`.
- Which kind: drawn with the weights as probabilities.
- Where: 60 random tiles per obstacle; the invalid ones are dropped (outside the world,
  overlapping, too close to the spawn point). The rest are scored with
  `difficulty · closeness_to_a_coin + (1 − difficulty) · random`, and the best one that does
  not cut off a reachable coin wins.

## Example

A new level, a player who wins without being hit and takes every coin:

| Run | Performance | Reward | Difficulty | Obstacle budget |
|---|---|---|---|---|
| 0 | | | 0.50 | 12 |
| 1 | 1.00 | 0.46 | 0.71 | 15 |
| 2 | 1.00 | 0.46 | 0.86 | 18 |
| 3 | 1.00 | 0.46 | 0.95 | 19 |

As the level fills with obstacles the player starts taking damage, performance drops towards
0.65 and the difficulty settles where the level stays challenging.
