# Save Compatibility Policy

This policy defines how version bumps affect player saves.

## Versioning
- Patch (`x.y.Z`): text fixes, minor numeric balance; save-safe.
- Minor (`x.Y.z`): new cards/relics/events; usually save-safe but may alter generated pools.
- Major (`X.y.z`): system-level mechanic changes; may break active runs.

## Compatibility guarantees
1. Never change published IDs for cards/relics/powers/events.
2. Avoid removing content referenced by existing saves.
3. If removal is necessary, keep tombstone mappings for one minor cycle.
4. Resource schema changes require migration code or major bump.

## Release notes requirements
- State whether active runs are safe.
- State whether existing save files are safe.
- Include rollback instructions to prior known-good version.

## Breaking-change protocol
- Mark release as `BREAKING SAVE CHANGE` in title.
- Keep previous stable build downloadable when possible.
- Provide migration notes and known failure modes.
