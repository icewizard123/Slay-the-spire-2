# Exiled Prince Implementation Backlog (Actionable)

This file converts the high-level concept into build tasks you can execute in order.

## Milestone 1: Bootstrapping
- Register character `EXILED_PRINCE`.
- Add custom color, card library page, and select-screen metadata.
- Load `keywords.json` into localization pipeline.

## Milestone 2: Core systems
- Implement Influence resource manager (0..10 clamp).
- Add helper APIs:
  - `gainInfluence(int amount)`
  - `spendInfluence(int amount)`
  - `canSpendInfluence(int amount)`
- Implement Rebellion state with per-turn upkeep callback.

## Milestone 3: Cards (v0.1)
- Implement starter cards first (`EX_STRIKE`, `EX_DEFEND`, `TACTICAL_BRIEFING`, `COMPEL`).
- Implement remaining commons/uncommons from `cards_v0_1.csv`.
- Gate Rare cards behind stability testing.

## Milestone 4: Relics
- Add `BLACK_SEAL` first (start-of-combat + first Order discount logic).
- Add three non-starter relics from `relics_v0_1.csv`.

## Milestone 5: Validation checklist
- Verify all card IDs resolve and localization keys are present.
- Simulate combat states where Influence is 0, 1, 9, 10.
- Ensure no soft-lock when `ABSOLUTE_COMMAND` is played vs bosses/elites.

## Milestone 6: Publish prep
- Add version + changelog.
- Add mod icon/banner with original artwork.
- Prepare Steam Workshop and Nexus descriptions using original names only.
