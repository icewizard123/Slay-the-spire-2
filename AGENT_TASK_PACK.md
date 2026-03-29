# Exiled Prince — Copy/Paste Task Pack for Parallel Agents

Use the tasks below as-is with other agents. Each task has a strict scope, deliverables, and acceptance tests.

---

## Task 1 — Character bootstrap + registration

**Paste this to Agent 1:**

```text
You are implementing the Exiled Prince character bootstrap.

Scope:
- Create runtime character registration for `EX_CHAR_EXILED_PRINCE`.
- Wire select-screen metadata and starter loadout from `design/exiled_prince/starter_kit.json`.
- Add placeholder art refs (do not add copyrighted assets).

Inputs:
- design/exiled_prince/starter_kit.json
- design/exiled_prince/id_conventions.md

Deliverables:
1) Character registration code
2) Starter deck/relic loading
3) Basic select-screen entry
4) README section: how to run with this character enabled

Acceptance checks:
- Game boots and character appears in selection.
- Starting deck matches starter_kit.json exactly.
- No crash entering first combat.
```

---

## Task 2 — Influence resource system + HUD

**Paste this to Agent 2:**

```text
Implement the Influence resource system for Exiled Prince.

Scope:
- Add Influence resource model with clamp 0..10.
- Add APIs: gainInfluence, spendInfluence, canSpendInfluence.
- Render Influence on HUD during combat.
- Emit events on gain/spend according to event bus spec.

Inputs:
- design/exiled_prince/starter_kit.json
- design/exiled_prince/status_effects_catalog.csv
- architecture/event_bus.md

Deliverables:
1) Resource model + tests
2) HUD indicator with current/max value
3) Event emission hooks

Acceptance checks:
- Influence never drops <0 or exceeds 10.
- HUD updates immediately when value changes.
- Save/load preserves current Influence value.
```

---

## Task 3 — Opcode interpreter (core 8 ops)

**Paste this to Agent 3:**

```text
Build a data-driven opcode interpreter for cards.

Scope:
- Implement opcode execution engine using `architecture/card_data_schema.yaml`.
- Support ops: DEAL_DAMAGE, GAIN_BLOCK, APPLY_DEBUFF, APPLY_BUFF, GAIN_RESOURCE, SPEND_RESOURCE, DRAW, ENTER_STATE.
- Ensure pipeline order follows `architecture/effect_pipeline.md`.

Inputs:
- architecture/card_data_schema.yaml
- architecture/effect_pipeline.md

Deliverables:
1) Opcode executor
2) Validation for malformed opcode args
3) Unit tests for each opcode

Acceptance checks:
- Deterministic output for same seed + state.
- Invalid opcodes fail gracefully with actionable error.
- Execution trace logging includes opcode + state delta.
```

---

## Task 4 — Card implementation from CSV

**Paste this to Agent 4:**

```text
Implement first-pass Exiled Prince cards from data.

Scope:
- Load and implement the first 10 cards from `design/exiled_prince/cards_v0_1.csv`.
- Ensure upgrades apply correctly.
- Ensure card text matches behavior.

Inputs:
- design/exiled_prince/cards_v0_1.csv
- design/exiled_prince/localization_en.template.json
- design/shared/keyword_registry.json

Deliverables:
1) Card classes/data bindings for 10 cards
2) Upgrade logic
3) Tooltip integration via shared keyword registry

Acceptance checks:
- All 10 cards playable in combat.
- Upgraded values match CSV definitions.
- No card-text mismatch in smoke test.
```

---

## Task 5 — Rebellion state + Order interactions

**Paste this to Agent 5:**

```text
Implement Rebellion and Order interaction rules.

Scope:
- Add Rebellion state with end-of-turn HP upkeep.
- Add Order potency bonus while Rebellion is active.
- Enforce status stacking/decay semantics per catalog.

Inputs:
- design/exiled_prince/status_effects_catalog.csv
- design/exiled_prince/keywords.json
- architecture/effect_pipeline.md

Deliverables:
1) Rebellion status implementation
2) Order potency modifier hook
3) Tests for upkeep and interaction edge-cases

Acceptance checks:
- Rebellion does not stack incorrectly.
- Order bonus applies only while Rebellion is active.
- Upkeep triggers once per player turn.
```

---

## Task 6 — Relics implementation

**Paste this to Agent 6:**

```text
Implement Exiled Prince relics from v0.1 data.

Scope:
- Implement BLACK_SEAL first.
- Implement remaining relics in `design/exiled_prince/relics_v0_1.csv`.
- Hook relic effects into event bus.

Inputs:
- design/exiled_prince/relics_v0_1.csv
- architecture/event_bus.md

Deliverables:
1) Relic logic + registration
2) Trigger subscriptions
3) Tests for one-time and per-turn effects

Acceptance checks:
- BLACK_SEAL grants start-of-combat Influence.
- First Order discount works once per combat.
- No duplicate trigger firings.
```

---

## Task 7 — Intent preview polish

**Paste this to Agent 7:**

```text
Implement enemy intent preview improvements.

Scope:
- Show exact deterministic values and modifier breakdown.
- Add unknown/random intent icons and tooltip language.
- Ensure live updates when combat modifiers change.

Inputs:
- ui/intent_preview_spec.md
- design/shared/keyword_registry.json

Deliverables:
1) UI update for intent panel/tooltips
2) Unknown/random visual assets (placeholder OK)
3) QA tests for value parity vs actual execution

Acceptance checks:
- Previewed damage equals executed damage in test suite.
- Unknown icon only used when uncertainty exists.
- Multi-hit and range intents render correctly.
```

---

## Task 8 — Save snapshots + crash recovery

**Paste this to Agent 8:**

```text
Implement save-state snapshot system.

Scope:
- Snapshot after each room and combat end.
- Keep rolling window (default 10 snapshots).
- Add crash recovery prompt to restore latest valid snapshot.

Inputs:
- architecture/save_snapshot_spec.md
- policy/save_compatibility_policy.md

Deliverables:
1) Snapshot writer/reader
2) Schema/version validator
3) Recovery flow in startup path

Acceptance checks:
- Snapshot corruption does not brick active save.
- Version mismatch shows clear user-facing message.
- Rollback restores deterministic replay state.
```

---

## Task 9 — QA automation + smoke suite

**Paste this to Agent 9:**

```text
Create automated smoke tests for Exiled Prince systems.

Scope:
- Add tests for character boot, starter combat, first 10 cards, Influence clamp, Rebellion upkeep, BLACK_SEAL behavior, and save/load.
- Mirror success criteria in qa/playtest_matrix.md.

Inputs:
- qa/playtest_matrix.md
- design/exiled_prince/cards_v0_1.csv
- design/exiled_prince/relics_v0_1.csv

Deliverables:
1) CI-runnable smoke suite
2) Test report format with pass/fail per scenario

Acceptance checks:
- Tests are deterministic with fixed seed.
- Failures include reproduction seed and scenario.
```

---

## Task 10 — Release prep + docs sync

**Paste this to Agent 10:**

```text
Prepare release artifacts for Steam Workshop and Nexus Mods.

Scope:
- Update changelog and versioning policy usage.
- Ensure README/install/uninstall and compatibility notes are present.
- Validate legal/IP checklist compliance.

Inputs:
- release/steam_nexus_checklist.md
- policy/save_compatibility_policy.md
- READINESS_REPORT.md

Deliverables:
1) Release notes template
2) Updated docs for install/uninstall/compatibility
3) Pre-release checklist with owner + status

Acceptance checks:
- All checklist items mapped to owner and state.
- Release notes include active-run/save compatibility statement.
```

---

## Integration manager prompt (for you)

Use this after agents submit PRs:

```text
You are the integration manager. Merge tasks in this order:
1) bootstrap/resource core (Tasks 1-3)
2) gameplay content (Tasks 4-6)
3) UX + persistence (Tasks 7-8)
4) tests + release docs (Tasks 9-10)

For each merge:
- Run relevant tests.
- Resolve ID conflicts using design/exiled_prince/id_conventions.md.
- Reject any change that breaks save compatibility without policy-compliant notes.
- Maintain deterministic behavior under fixed seed.
```
