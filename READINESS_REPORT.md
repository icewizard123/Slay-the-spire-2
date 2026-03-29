# Exiled Prince Readiness Report

## Short answer
**No — not playable yet.**

Current repository state is design/spec complete, but runtime implementation is missing.

## What is ready
- Character design direction, mechanics, and balancing intent.
- Card/relic/event data tables and naming conventions.
- UX/system architecture specs (intent previews, event bus, effect pipeline).
- QA/release process documents and save-compatibility policy.

## What is NOT ready (blocking)
1. No executable mod/plugin code exists yet.
2. No runtime integration for:
   - Character registration
   - Influence resource meter rendering and logic
   - Order/Rebellion status resolution
   - Data loader for card/relic JSON/CSV/YAML assets
3. No card/relic classes or opcode interpreter implementation.
4. No localization loader wiring to the game UI.
5. No automated tests or simulation harness.
6. No actual art/audio assets included.

## Definition of "ready to playtest"
The character is ready for internal playtest only after all of the following are true:
- Game boots with character selectable.
- Starter deck + starter relic load and function.
- At least 10 cards and 3 relics are executable in combat.
- Influence clamps correctly and is visible in UI.
- Rebellion upkeep and Order interactions resolve deterministically.
- Run can complete Act 1 without crashes/soft-locks.

## Recommended next implementation slice (MVP)
1. Implement character registration + select-screen entry.
2. Implement Influence resource model + HUD widget.
3. Implement opcode interpreter for 8 core ops:
   - DEAL_DAMAGE
   - GAIN_BLOCK
   - APPLY_DEBUFF
   - APPLY_BUFF
   - GAIN_RESOURCE
   - SPEND_RESOURCE
   - DRAW
   - ENTER_STATE
4. Implement first 10 cards from `cards_v0_1.csv`.
5. Implement `BLACK_SEAL` and one uncommon relic.
6. Add smoke tests:
   - Boot + load character
   - Play each starter card once
   - Save/load mid-combat state

## Release readiness gate
Do not publish to Steam/Nexus until:
- 30+ full runs logged with no critical bugs.
- Card text/behavior mismatch rate is 0 in QA sample.
- Save compatibility statement included in release notes.
