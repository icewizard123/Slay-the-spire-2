# Exiled Prince ID Conventions

Use stable IDs from day one to avoid save incompatibilities.

## Prefixes
- Character: `EX_CHAR_`
- Cards: `EX_CARD_`
- Relics: `EX_RELIC_`
- Powers/Statuses: `EX_POWER_`
- Events: `EX_EVENT_`
- Keywords: `EX_KEYWORD_`

## Examples
- Character ID: `EX_CHAR_EXILED_PRINCE`
- Card ID: `EX_CARD_COMPEL`
- Relic ID: `EX_RELIC_BLACK_SEAL`
- Power ID: `EX_POWER_REBELLION`
- Event ID: `EX_EVENT_COUNCIL_RIFT`
- Keyword ID: `EX_KEYWORD_INFLUENCE`

## Rules
1. IDs are ALL_CAPS snake case.
2. IDs are immutable once published.
3. Renames must preserve old IDs and map display names via localization.
4. Never reuse a removed ID for new content.
5. Keep IDs and localization keys 1:1 where possible.
