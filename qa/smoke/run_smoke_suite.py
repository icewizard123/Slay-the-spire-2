from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from qa.smoke.exiled_prince_smoke import as_report_rows, run_all_scenarios


def main() -> int:
    report_path = Path("qa/smoke/latest_report.json")

    try:
        results = run_all_scenarios()
    except AssertionError as exc:
        print(f"SMOKE SUITE FAILED: {exc}")
        return 1

    rows = as_report_rows(results)
    report_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    print("| Scenario | Seed | Status | Details |")
    print("|---|---:|---|---|")
    for row in rows:
        status = "PASS" if row["passed"] else "FAIL"
        print(f"| {row['scenario']} | {row['seed']} | {status} | {row['details']} |")

    if all(row["passed"] for row in rows):
        print(f"\nWrote scenario report to {report_path}")
        return 0

    print(f"\nOne or more scenarios failed. See {report_path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
