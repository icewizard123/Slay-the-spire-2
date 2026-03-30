# Unified Combat Event Bus

## Core events
- Turn lifecycle: `TurnStart`, `TurnEnd`
- Card lifecycle: `OnDraw`, `OnPlay`, `OnExhaust`, `OnDiscard`
- Combat math: `OnDamageDealt`, `OnDamageTaken`, `OnBlockGained`
- Status lifecycle: `OnBuffApplied`, `OnDebuffApplied`, `OnStatusRemoved`
- Resource lifecycle: `OnInfluenceGained`, `OnInfluenceSpent`

## Event payload contract
- `source_id`
- `target_id`
- `event_type`
- `value` (optional numeric)
- `tags` (list)
- `timestamp`
- `combat_seed_frame`

## Subscription rules
- Subscribers declare priority (higher runs first).
- Event handlers must be side-effect scoped and idempotent when possible.
- Prevent infinite loops via max re-emit depth guard.

## Benefits
- Removes ad-hoc trigger wiring.
- Makes relic/power/card interactions composable.
- Enables combat log playback and deterministic debugging.
