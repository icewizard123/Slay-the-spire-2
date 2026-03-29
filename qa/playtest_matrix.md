# Exiled Prince Playtest Matrix

## Coverage matrix

| Scenario | Seed Runs | Pass Criteria |
|---|---:|---|
| Starter deck Act 1 survival | 10 | Reach first boss in >= 70% runs |
| Influence generation stress | 5 | Influence remains clamped between 0 and 10 |
| Order-heavy build | 10 | No non-interactive enemy lock pattern |
| Rebellion build | 10 | HP upkeep meaningful but not auto-lose |
| Rare-card spike turns | 5 | No deterministic OTK before intended pacing |

## Bug checklist
- Card text matches behavior for every upgraded card.
- Save/load roundtrip keeps Influence and Rebellion state.
- Enemy intent manipulation works on standard + boss intents.
- Relic triggers fire once per expected condition.

## Telemetry to track
- Average Influence spent per combat.
- Pick rate per card/relic.
- Death cause (chip damage, burst, status clutter).
- Turn count per elite/boss fight.
