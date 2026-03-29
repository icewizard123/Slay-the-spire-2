# Effect Resolution Pipeline

Normalize effect order to remove interaction ambiguity.

## Canonical order
1. `onPlay` hooks (card/relic/power pre-resolution)
2. Target resolution/validation
3. Cost and resource spend
4. Base effect opcode execution
5. Damage/block/debuff calculations
6. Reactive triggers (`OnDamageDealt`, `OnDebuffApplied`, etc.)
7. Post-play hooks (`AfterCardPlayed`)
8. Zone cleanup (discard/exhaust/retain)
9. End-of-action state reconciliation

## Invariants
- If target becomes invalid before step 4, skip target-dependent opcodes only.
- Reactive triggers must not mutate already-resolved damage packets.
- Deterministic random seeds are consumed at defined opcode boundaries only.

## Debugging
- Emit a per-card "resolution trace" log entry with step timestamps.
- Include IDs for actor, target(s), opcode, and resulting state deltas.
