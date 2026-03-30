#!/usr/bin/env bash
set -euo pipefail

# Wrapper so users can run from repo root with:
#   bash run_preflight_checks.sh

if [[ -f "scripts/run_preflight_checks.sh" ]]; then
  bash scripts/run_preflight_checks.sh
  exit 0
fi

echo "ERROR: scripts/run_preflight_checks.sh not found."
echo "Make sure you are in the repository root (Slay-the-spire-2)."
echo "Current directory: $(pwd)"
echo "Tip (Codespaces): cd /workspaces/Slay-the-spire-2 && bash run_preflight_checks.sh"
exit 1
