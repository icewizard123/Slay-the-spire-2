# Exiled Prince — How to Test If It Works

This guide assumes you merged all implementation PRs from `AGENT_TASK_PACK.md`.

## 0) Preflight (before launching)

- Confirm your branch includes runtime code (not only docs/specs).
- Confirm all IDs in code match `design/exiled_prince/id_conventions.md`.
- Confirm data files parse successfully (JSON/CSV/YAML).

### Quick validation commands
```bash
python -m json.tool design/exiled_prince/starter_kit.json >/dev/null
python -m json.tool design/exiled_prince/keywords.json >/dev/null
python -m json.tool design/exiled_prince/localization_en.template.json >/dev/null
python -m json.tool design/shared/keyword_registry.json >/dev/null
python - <<'PY'
import csv
for p in [
  'design/exiled_prince/cards_v0_1.csv',
  'design/exiled_prince/relics_v0_1.csv',
  'design/exiled_prince/events_v0_1.csv',
  'design/exiled_prince/status_effects_catalog.csv',
  'design/exiled_prince/reward_weights_v0_1.csv',
]:
    with open(p, newline='') as f:
        list(csv.reader(f))
print('csv ok')
PY
```

---

## 1) Smoke test (10–15 minutes)

## A. Character boot test
1. Launch game with mod enabled.
2. On character select, verify `The Exiled Prince` appears.
3. Start run.

**Pass if:** no crash and character is selectable.

## B. Starter deck/relic test
1. Open deck immediately in run.
2. Verify starter deck matches `starter_kit.json` exactly.
3. Enter first combat.
4. Verify `Black Seal` grants start-of-combat Influence.

**Pass if:** starter setup is exact and relic trigger fires once.

## C. Influence clamp test
1. Play cards/relic effects that gain Influence repeatedly.
2. Verify Influence never goes above 10.
3. Spend Influence until 0.
4. Verify it never drops below 0.

**Pass if:** clamp is always `0..10`.

## D. Rebellion + Order interaction test
1. Enter Rebellion state.
2. Play Order card(s).
3. Confirm potency bonus applies while Rebellion is active.
4. End turn and confirm upkeep HP loss triggers once.

**Pass if:** bonus and upkeep behavior match spec.

---

## 2) Determinism and pipeline test

1. Set fixed seed.
2. Run same scripted combat scenario twice.
3. Compare combat logs/resolution traces.

**Pass if:** outputs are identical.

Also verify card resolution ordering follows:
`onPlay -> target select -> cost/resource spend -> opcodes -> damage/debuff calc -> triggers -> cleanup`.

---

## 3) Intent preview verification

1. Inspect enemy deterministic attack intent.
2. Confirm preview shows base/modifiers/final values.
3. Apply Weak/Vulnerable/Strength changes mid-turn.
4. Confirm preview updates live.
5. Trigger uncertain intent state and verify unknown/random icon.

**Pass if:** shown values match executed values.

---

## 4) Save/load + snapshot recovery test

1. Start run, finish a room, then save and quit.
2. Reload and verify player/map/resource state is preserved.
3. Force crash/test failure scenario (dev mode) and restart.
4. Verify recovery prompt appears and restore works.

**Pass if:** state restores correctly, no save corruption.

---

## 5) 30-run stability gate (before release)

Track in your QA sheet:
- Crash rate
- Soft-lock count
- Card text/behavior mismatch count
- Average Influence spent/combat
- Win rate by difficulty

**Release recommendation:** only ship when critical bugs are 0 and card-text mismatch is 0 in sampled runs.

---

## 6) If a test fails, file bug with this template

```text
Title: [Exiled Prince] <short issue>
Build: <version/commit>
Seed: <seed>
Scenario: <where it happened>
Expected: <expected behavior>
Actual: <actual behavior>
Repro steps:
1) ...
2) ...
3) ...
Logs/trace:
- attach combat log
- attach screenshot/video if UI issue
```
