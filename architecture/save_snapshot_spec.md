# Save-State Snapshot Spec

## Snapshot cadence
- Persist snapshot after each room resolution.
- Persist snapshot after each combat end.
- Optional debug mode: snapshot each turn.

## Snapshot contents
- Player state (HP, gold, deck, relics, statuses, resources)
- Map progression and route
- RNG seed + frame index
- Current room/combat metadata
- Registered mod version and schema version

## Storage
- Keep rolling window of last N snapshots (default: 10).
- Compress snapshots with checksum.
- Mark incompatible snapshots with explicit version mismatch reason.

## Recovery flows
1. Manual rollback to previous snapshot from menu.
2. Crash recovery prompt on startup if latest snapshot is valid.
3. Developer replay mode loads snapshot + deterministic seed.

## Guardrails
- Snapshot write failures should not corrupt active save.
- Validate schema before load; reject with user-friendly message.
