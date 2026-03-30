# Slay-the-spire-2

## Exiled Prince bootstrap

This repository now includes a runtime bootstrap for the Exiled Prince character using stable IDs from `design/exiled_prince/id_conventions.md`.

### What is wired
- Character registration under `EX_CHAR_EXILED_PRINCE`.
- Select-screen metadata (name/title/flavor + placeholder art references).
- Starter loadout from `design/exiled_prince/starter_kit.json`:
  - Gold: `99`
  - Relic: `EX_RELIC_BLACK_SEAL`
  - Deck (exact order):
    - `EX_CARD_EX_STRIKE` ×4
    - `EX_CARD_EX_DEFEND` ×4
    - `EX_CARD_TACTICAL_BRIEFING` ×1
    - `EX_CARD_COMPEL` ×1

### Run with Exiled Prince enabled
From repository root:

```bash
python -m runtime.exiled_prince_bootstrap
```

Expected output:

```text
Registered characters: EX_CHAR_EXILED_PRINCE
```

### Validation commands
```bash
pytest -q
```

The tests validate registration, select-screen metadata presence, and starter deck/relic parity with the starter kit.

### Placeholder art
Art is intentionally non-copyrighted placeholders at:
- `assets/placeholders/exiled_prince_art_refs.json`

Replace these refs with licensed/original assets before shipping.
