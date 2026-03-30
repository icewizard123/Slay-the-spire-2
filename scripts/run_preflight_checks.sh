#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] JSON validation"
python -m json.tool design/exiled_prince/starter_kit.json >/dev/null
python -m json.tool design/exiled_prince/keywords.json >/dev/null
python -m json.tool design/exiled_prince/localization_en.template.json >/dev/null
python -m json.tool design/shared/keyword_registry.json >/dev/null
echo "  OK: JSON files"

echo "[2/3] CSV validation"
python - <<'PY'
import csv
paths = [
  'design/exiled_prince/cards_v0_1.csv',
  'design/exiled_prince/relics_v0_1.csv',
  'design/exiled_prince/events_v0_1.csv',
  'design/exiled_prince/status_effects_catalog.csv',
  'design/exiled_prince/reward_weights_v0_1.csv',
]
for p in paths:
    with open(p, newline='') as f:
        rows = list(csv.reader(f))
        if not rows:
            raise SystemExit(f"CSV is empty: {p}")
print('  OK: CSV files')
PY

echo "[3/3] Required docs/spec files present"
required=(
  AGENT_TASK_PACK.md
  IMPLEMENTATION_BACKLOG.md
  MODDING_PLAN_LELOUCH.md
  READINESS_REPORT.md
  TESTING_GUIDE.md
  architecture/card_data_schema.yaml
  architecture/effect_pipeline.md
  architecture/event_bus.md
  architecture/save_snapshot_spec.md
  qa/playtest_matrix.md
  release/steam_nexus_checklist.md
)
for f in "${required[@]}"; do
  [[ -f "$f" ]] || { echo "Missing required file: $f"; exit 1; }
done
echo "  OK: required files"

echo "PASS: preflight checks complete"
