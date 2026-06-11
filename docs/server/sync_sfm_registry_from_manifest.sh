#!/usr/bin/env bash
# B-SFM-W06b — sync canonical registry → legacy path (cp, not symlink).
set -euo pipefail

ROOT="${ALADDIN_BACKEND_ROOT:-/opt/aladdin-backend}"
MANIFEST="${ROOT}/data/sfm/function_registry.manifest.json"
CANONICAL="${ROOT}/app/data/sfm/function_registry.json"
LEGACY="${ROOT}/data/sfm/function_registry.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "FAIL: manifest missing: $MANIFEST" >&2
  exit 1
fi

canonical_manifest=$(python3 -c "import json;print(json.load(open('$MANIFEST'))['canonical_path'])")
if [[ -f "$canonical_manifest" ]]; then
  CANONICAL="$canonical_manifest"
fi

if [[ ! -f "$CANONICAL" ]]; then
  echo "FAIL: canonical registry missing: $CANONICAL" >&2
  exit 1
fi

mkdir -p "$(dirname "$LEGACY")"
cp -f "$CANONICAL" "$LEGACY"

count=$(python3 -c "
import json
d=json.load(open('$CANONICAL'))
if isinstance(d, dict) and 'functions' in d:
    print(len(d['functions']))
else:
    print(len(d))
")
sha=$(sha256sum "$CANONICAL" | awk '{print $1}')
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)

python3 - <<PY
import json
from pathlib import Path
manifest = Path("$MANIFEST")
data = json.loads(manifest.read_text())
data["canonical_path"] = "$CANONICAL"
data["legacy_sync_path"] = "$LEGACY"
data["functions_count"] = int("$count")
data["sha256"] = "$sha"
data["updated_at"] = "$now"
data["last_sync"] = "$now"
manifest.write_text(json.dumps(data, indent=2) + "\n")
print(json.dumps({"pass": True, "canonical": "$CANONICAL", "legacy": "$LEGACY", "functions_count": int("$count"), "sha256": "$sha"}, indent=2))
PY
