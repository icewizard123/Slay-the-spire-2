#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR="$ROOT_DIR/build_artifacts"
SRC_DIR="$ROOT_DIR/build_src"

mkdir -p "$ARTIFACT_DIR"

gcc -shared -fPIC "$SRC_DIR/baselib.c" -o "$ARTIFACT_DIR/baselib.dll"
gcc -shared -fPIC "$SRC_DIR/exiled_prince.c" -o "$ARTIFACT_DIR/exiled_prince.dll"

python - <<'PY'
from pathlib import Path
import zipfile
root = Path('build_artifacts')
with zipfile.ZipFile(root / 'baselib.pck', 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.write(root / 'baselib.json', arcname='baselib.json')
    z.write(root / 'baselib.dll', arcname='baselib.dll')
with zipfile.ZipFile(root / 'exiled_prince.pck', 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.write(root / 'exiled_prince.json', arcname='exiled_prince.json')
    z.write(root / 'exiled_prince.dll', arcname='exiled_prince.dll')
    z.write('design/exiled_prince/starter_kit.json', arcname='content/starter_kit.json')
    z.write('design/exiled_prince/localization_en.template.json', arcname='content/localization_en.template.json')
    z.write('design/exiled_prince/cards_v0_1.csv', arcname='content/cards_v0_1.csv')
    z.write('design/exiled_prince/relics_v0_1.csv', arcname='content/relics_v0_1.csv')
PY

(
  cd "$ARTIFACT_DIR"
  sha256sum baselib.dll baselib.json baselib.pck exiled_prince.dll exiled_prince.json exiled_prince.pck > checksums.sha256
)

echo "Artifacts generated in $ARTIFACT_DIR"
